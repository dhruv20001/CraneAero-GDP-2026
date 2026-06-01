import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np
import open3d as o3d
from std_msgs.msg import Header
import time


class VoxelFilterOptimized(Node):
    def __init__(self):
        super().__init__('voxel_filter')
        
        # Parameters
        self.declare_parameter('voxel_size', 0.05)
        self.declare_parameter('max_points', 20000)  # Reduced from 50k
        self.declare_parameter('enable_statistical_filter', False)
        self.declare_parameter('drop_old_messages', True)
        
        self.voxel_size = self.get_parameter('voxel_size').value
        self.max_points = self.get_parameter('max_points').value
        self.enable_stat_filter = self.get_parameter('enable_statistical_filter').value
        self.drop_old = self.get_parameter('drop_old_messages').value
        
        # CRITICAL: Aggressive QoS for LOW LATENCY
        # ReliabilityPolicy.BEST_EFFORT = No resends, drop messages if necessary
        # HistoryPolicy.KEEP_LAST with depth=1 = Only buffer 1 message
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,  # ⚠️ CRITICAL: depth=1 prevents message queuing
            liveliness_lease_duration_ms=5000
        )
        
        self.subscription = self.create_subscription(
            PointCloud2, 
            '/fused_cloud', 
            self.cloud_callback, 
            qos_profile
        )
        
        self.publisher = self.create_publisher(
            PointCloud2, 
            '/filtered_cloud', 
            qos_profile
        )
        
        # Metrics
        self.callback_count = 0
        self.dropped_count = 0
        self.last_log_time = time.time()
        
        self.get_logger().info(
            f'VoxelFilter (OPTIMIZED): voxel_size={self.voxel_size}m, '
            f'max_points={self.max_points}, drop_old_msgs={self.drop_old}'
        )

    def cloud_callback(self, msg):
        """Fast point cloud processing with minimal latency."""
        
        # Optional: Drop old messages if processing can't keep up
        if self.drop_old:
            current_time = self.get_clock().now()
            msg_time = rclpy.time.Time.from_msg(msg.header.stamp)
            message_age = (current_time - msg_time).nanoseconds / 1e9
            
            # Drop messages older than 100ms
            if message_age > 0.1:
                self.dropped_count += 1
                if self.dropped_count % 50 == 0:
                    self.get_logger().warn(
                        f'Dropped {self.dropped_count} old messages '
                        f'(age > 100ms)'
                    )
                return
        
        try:
            start = time.time()
            
            # FAST PATH: Read points directly without intermediate list
            points_list = []
            count = 0
            for point in pc2.read_points(msg, skip_nans=True):
                points_list.append([point[0], point[1], point[2]])
                count += 1
                if count >= self.max_points:
                    break
            
            if len(points_list) == 0:
                return
            
            # Convert to numpy in one go
            points = np.array(points_list, dtype=np.float32)
            
            # Create and filter cloud (Open3D is generally fast here)
            cloud = o3d.geometry.PointCloud()
            cloud.points = o3d.utility.Vector3dVector(points)
            
            # Voxel downsample (this is usually the slowest step)
            filtered = cloud.voxel_down_sample(self.voxel_size)
            filtered_points = np.asarray(filtered.points, dtype=np.float32)
            
            # Create message with current timestamp (not message timestamp)
            header = Header()
            header.frame_id = msg.header.frame_id
            header.stamp = self.get_clock().now().to_msg()
            
            # Create and publish immediately
            cloud_msg = pc2.create_cloud_xyz32(header, filtered_points)
            self.publisher.publish(cloud_msg)
            
            # Update metrics (lightweight)
            self.callback_count += 1
            elapsed = (time.time() - start) * 1000
            
            # Log every 2 seconds
            current_time = time.time()
            if current_time - self.last_log_time > 2.0:
                self.get_logger().info(
                    f'Processed {self.callback_count} clouds | '
                    f'Last latency: {elapsed:.2f}ms | '
                    f'Points: {len(points)} -> {len(filtered_points)}'
                )
                self.last_log_time = current_time
            
        except Exception as e:
            self.get_logger().error(f'Processing error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = VoxelFilterOptimized()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()