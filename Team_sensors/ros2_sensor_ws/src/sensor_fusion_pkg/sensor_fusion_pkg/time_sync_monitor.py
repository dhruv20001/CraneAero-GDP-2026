#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from message_filters import Subscriber, ApproximateTimeSynchronizer
import collections
import math
import numpy as np


class TimeSyncCompensator(Node):

    def __init__(self):
        super().__init__('time_sync_compensator')

        # Declare parameters
        self.declare_parameter('queue_size', 30)
        self.declare_parameter('slop', 0.5)
        self.declare_parameter('stats_window', 100)
        self.declare_parameter('regression_window', 50)
        self.declare_parameter('apply_correction', True)
        self.declare_parameter('publish_corrected_topics', True)

        queue_size = self.get_parameter('queue_size').value
        slop = self.get_parameter('slop').value
        self.stats_window = self.get_parameter('stats_window').value
        self.regression_window = self.get_parameter('regression_window').value
        self.apply_correction = self.get_parameter('apply_correction').value
        self.publish_corrected = self.get_parameter('publish_corrected_topics').value

        # Subscribers (raw topics)
        self.lidar_sub = Subscriber(self, LaserScan, '/scan')
        self.camera_sub = Subscriber(self, Image, '/camera/camera/color/image_raw')

        # Synchronizer
        self.ts = ApproximateTimeSynchronizer(
            [self.lidar_sub, self.camera_sub],
            queue_size,
            slop
        )
        self.ts.registerCallback(self.synced_callback)

        # Publishers for corrected topics (if enabled)
        if self.publish_corrected:
            self.lidar_corrected_pub = self.create_publisher(LaserScan, '/scan_corrected', 10)
            self.camera_corrected_pub = self.create_publisher(Image, '/camera/image_raw_corrected', 10)

        # Storage for calibration
        self.errors = collections.deque(maxlen=self.stats_window)
        self.time_pairs = collections.deque(maxlen=self.regression_window)  # (avg_time, error)
        
        # Correction model parameters
        self.drift_rate = 0.0  # ms per second
        self.offset = 0.0      # ms at reference time
        self.reference_time = None
        self.model_updated = False

        # Timer for statistics
        self.create_timer(10.0, self.print_statistics)

        self.get_logger().info("Time Sync Compensator Started - Will actively correct timestamps")

    def synced_callback(self, lidar_msg, camera_msg):

        # Original timestamps
        lidar_time = lidar_msg.header.stamp.sec + lidar_msg.header.stamp.nanosec * 1e-9
        camera_time = camera_msg.header.stamp.sec + camera_msg.header.stamp.nanosec * 1e-9

        # Compute raw error
        raw_error_ms = (lidar_time - camera_time) * 1000.0
        self.errors.append(raw_error_ms)

        # Update drift model
        avg_time = (lidar_time + camera_time) / 2.0
        self.time_pairs.append((avg_time, raw_error_ms))
        
        if len(self.time_pairs) >= 10:
            self.update_drift_model()

        # Apply correction if model is available
        if self.apply_correction and self.model_updated:
            corrected_lidar_msg, corrected_camera_msg = self.correct_timestamps(
                lidar_msg, camera_msg, avg_time, raw_error_ms
            )
            
            # Publish corrected messages
            if self.publish_corrected:
                self.lidar_corrected_pub.publish(corrected_lidar_msg)
                self.camera_corrected_pub.publish(corrected_camera_msg)
                
            corrected_error = self.get_corrected_error(avg_time, raw_error_ms)
            self.get_logger().info(
                f"Raw: {raw_error_ms:.3f} ms | Corrected: {corrected_error:.3f} ms"
            )
        else:
            # Just monitor if not correcting
            self.get_logger().info(
                f"Synced Pair - Time Error: {raw_error_ms:.3f} ms"
            )

    def update_drift_model(self):
        """Perform linear regression to estimate drift and offset"""
        times, errors = zip(*self.time_pairs)
        times = np.array(times)
        errors = np.array(errors)

        # Linear regression: error = drift * (t - t0) + offset
        try:
            # Use first time as reference
            t0 = times[0]
            coeffs = np.polyfit(times - t0, errors, 1)
            self.drift_rate = coeffs[0]  # ms per second
            self.offset = coeffs[1]      # ms at t0
            self.reference_time = t0
            self.model_updated = True
            
            self.get_logger().info(
                f"Model updated: Offset={self.offset:.3f} ms, Drift={self.drift_rate:.3f} ms/s"
            )
        except Exception as e:
            self.get_logger().error(f"Model update failed: {e}")

    def correct_timestamps(self, lidar_msg, camera_msg, current_time, raw_error):
        """Apply correction to message timestamps"""
        
        # Calculate predicted error at current time
        if self.reference_time is not None:
            predicted_error = self.offset + self.drift_rate * (current_time - self.reference_time)
        else:
            predicted_error = raw_error

        # Decide which sensor to adjust (usually adjust camera to match LiDAR)
        # Option 1: Adjust camera timestamp
        corrected_camera_msg = camera_msg
        corrected_camera_msg.header.stamp.sec = int(current_time - predicted_error/1000.0)
        corrected_camera_msg.header.stamp.nanosec = int((current_time - predicted_error/1000.0 - int(current_time - predicted_error/1000.0)) * 1e9)
        
        # Option 2: Could also adjust LiDAR - choose based on your setup
        corrected_lidar_msg = lidar_msg  # Keep LiDAR as reference

        return corrected_lidar_msg, corrected_camera_msg

    def get_corrected_error(self, current_time, raw_error):
        """Calculate what the error would be after correction"""
        if self.reference_time is not None:
            predicted_error = self.offset + self.drift_rate * (current_time - self.reference_time)
            return raw_error - predicted_error
        return raw_error

    def print_statistics(self):
        if not self.errors:
            return

        n = len(self.errors)
        mean = sum(self.errors) / n
        variance = sum((x - mean) ** 2 for x in self.errors) / (n - 1) if n > 1 else 0.0
        stddev = math.sqrt(variance)

        self.get_logger().info(
            f"Statistics (last {n} pairs): "
            f"Mean = {mean:.3f} ms, StdDev = {stddev:.3f} ms"
        )
        
        if self.model_updated:
            self.get_logger().info(
                f"Active correction: Offset={self.offset:.3f} ms, Drift={self.drift_rate:.3f} ms/s"
            )


def main(args=None):
    rclpy.init(args=args)
    node = TimeSyncCompensator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()