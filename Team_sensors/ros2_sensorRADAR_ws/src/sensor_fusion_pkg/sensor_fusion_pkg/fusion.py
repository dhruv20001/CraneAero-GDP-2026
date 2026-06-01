#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
from std_msgs.msg import Header
from tf2_ros import Buffer, TransformListener
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud

class FuseClouds(Node):
    def __init__(self):
        super().__init__("fusion_node")

        self.cam = None
        self.radar = None
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_subscription(
            PointCloud2,
            "/camera_filtered",
            self.cam_cb,
            10
        )

        self.create_subscription(
            PointCloud2,
            "/radar_filtered",
            self.radar_cb,
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

    def radar_cb(self, msg):
        self.radar = msg
        self.try_publish()

    def try_publish(self):
        if self.cam is None or self.radar is None:
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                self.cam.header.frame_id,
                self.radar.header.frame_id,
                rclpy.time.Time()
            )
            
            transformed_radar = do_transform_cloud(self.radar, transform)
            
            cam_pts = list(pc2.read_points(self.cam, field_names=("x", "y", "z"), skip_nans=True))
            radar_pts = list(pc2.read_points(transformed_radar, field_names=("x", "y", "z"), skip_nans=True))

            fused = cam_pts + radar_pts
            
            self.get_logger().info(f"Fused: {len(cam_pts)} camera + {len(radar_pts)} radar = {len(fused)} points")

            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = self.cam.header.frame_id

            cloud = pc2.create_cloud_xyz32(header, fused)
            self.pub.publish(cloud)
            
        except Exception as e:
            self.get_logger().error(f"Transform error: {e}")

def main():
    rclpy.init()
    node = FuseClouds()
    rclpy.spin(node)

if __name__ == "__main__":
    main()