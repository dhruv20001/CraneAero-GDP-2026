#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, PointCloud2
from laser_geometry import LaserProjection

import tf2_ros
from tf2_ros import TransformListener, Buffer


class LidarToCloud(Node):

    def __init__(self):
        super().__init__("lidar_to_cloud")

        self.pub = self.create_publisher(PointCloud2, "/lidar_points", 10)
        self.sub = self.create_subscription(LaserScan, "/scan", self.cb, 10)

        self.proj = LaserProjection()

        # TF listener (required)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.get_logger().info("Publishing /lidar_points")

    def cb(self, scan: LaserScan):

        try:
            cloud = self.proj.projectLaser(scan)
            self.pub.publish(cloud)

        except Exception as e:
            self.get_logger().warn(f"Projection failed: {e}")


def main(args=None):

    rclpy.init(args=args)

    node = LidarToCloud()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()