from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # 1. LiDAR with RViz
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 256 000 ,
                'frame_id': 'laser',
                'angle_compensate': True,
                'scan_mode': 'Standard',
            }],
            output='screen',
        ),
        
        # 2. RealSense Camera with point cloud enabled
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            parameters=[{
                'enable_depth': True,
                'enable_color': True,
                'enable_pointcloud': True,
                'pointcloud.enable': True,
                'align_depth.enable': True,
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '640x480x30',
                'enable_sync': True,
            }],
            output='screen',
        ),
        
        # 3. Static Transform (LiDAR to Camera)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'camera_link', 'laser'],
            output='screen',
        ),
        
        # 4. LiDAR to PointCloud converter
        Node(
            package='sensor_fusion_pkg',
            executable='lidar_to_pointcloud',
            name='lidar_to_pointcloud',
            output='screen',
        ),
        
        # 5. Fusion Node
        Node(
            package='sensor_fusion_pkg',
            executable='fusion',
            name='fusion',
            output='screen',
        ),
        
        # 6. PassThrough Filter
        Node(
            package='pointcloud_filter',
            executable='passthrough_filter_node',
            name='passthrough',
            parameters=[{
                'min_x': -5.0, 'max_x': 5.0,
                'min_y': -5.0, 'max_y': 5.0,
                'min_z': 0.0, 'max_z': 3.0,
                'input_topic': '/fused_cloud',
                'output_topic': '/filtered_cloud',
            }],
            output='screen',
        ),
        
        # 7. Voxel Filter
        Node(
            package='pointcloud_filter',
            executable='voxel_grid_filter_node',
            name='voxel_grid',
            parameters=[{
                'voxel_size': 0.05,
                'input_topic': '/filtered_cloud',
                'output_topic': '/voxel_filtered',
            }],
            output='screen',
        ),
        
        # 8. RViz2 (optional - comment out if not needed)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(
                os.path.expanduser('~'), 
                'ros2_sensor_ws/src/sensor_fusion_pkg/config/fusion.rviz'
            )] if os.path.exists(os.path.expanduser('~/ros2_sensor_ws/src/sensor_fusion_pkg/config/fusion.rviz')) else [],
            output='screen',
        ),
    ])