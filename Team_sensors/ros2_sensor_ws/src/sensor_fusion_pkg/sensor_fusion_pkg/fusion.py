#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from std_msgs.msg import Header
from tf2_ros import Buffer, TransformListener
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud
import tf2_geometry_msgs


class FuseClouds(Node):
    def __init__(self):
        super().__init__("fuse_clouds")

        self.cam = None
        self.lidar = None
        
        # Initialize TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(
            PointCloud2,
            "/camera/camera/depth/color/points",
            self.cam_cb,
            10
        )

        self.create_subscription(
            PointCloud2,
            "/lidar_points",
            self.lidar_cb,
            10
        )

        self.pub = self.create_publisher(
            PointCloud2,
            "/fused_cloud",
            10
        )

        self.get_logger().info("Fusion node started")

    def cam_cb(self, msg):
        self.cam = msg
        self.try_publish()

    def lidar_cb(self, msg):
        self.lidar = msg
        self.try_publish()

    def try_publish(self):
        if self.cam is None or self.lidar is None:
            return

        try:
            # Get transform from lidar frame to camera frame
            transform = self.tf_buffer.lookup_transform(
                self.cam.header.frame_id,  # target: camera frame
                self.lidar.header.frame_id,  # source: lidar frame
                rclpy.time.Time()
            )
            
            # Transform lidar cloud to camera frame
            transformed_lidar = do_transform_cloud(self.lidar, transform)
            
            # Read points from both clouds (now both in camera frame)
            cam_pts = list(pc2.read_points(
                self.cam,
                field_names=("x", "y", "z"),
                skip_nans=True
            ))

            lidar_pts = list(pc2.read_points(
                transformed_lidar,
                field_names=("x", "y", "z"),
                skip_nans=True
            ))

            fused = cam_pts + lidar_pts

            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = self.cam.header.frame_id

            cloud = pc2.create_cloud_xyz32(header, fused)
            self.pub.publish(cloud)
            
        except Exception as e:
            self.get_logger().warn(f"Could not transform lidar to camera frame: {e}")


def main():
    rclpy.init()
    node = FuseClouds()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
    
    #practice github
