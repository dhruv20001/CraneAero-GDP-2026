from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. LiDAR
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 256000,
                'frame_id': 'laser',
                'angle_compensate': True,
                'scan_mode': 'Standard',
            }],
            output='screen',
        ),
        
        # 2. LiDAR to PointCloud converter
        Node(
            package='sensor_fusion_pkg',
            executable='lidar_to_pointcloud',
            name='lidar_to_pointcloud',
            output='screen',
        ),

        # 3. Camera
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            parameters=[{
                'enable_depth': True,
                'enable_color': True,
                'enable_pointcloud': True,
                'pointcloud.enable': True,
                'depth_module.profile': '640x480x30',
            }],
            output='screen',
        ),
        
        # 4. Fusion Node
        Node(
            package='sensor_fusion_pkg',
            executable='fusion',
            name='fusion',
            output='screen',
        ),
        
        # 5. Passthrough Filter
        Node(
            package='pointcloud_filter',
            executable='passthrough_filter_node',
            name='passthrough',
            parameters=[{
                'min_x': -5.0, 'max_x': 5.0,
                'min_y': -5.0, 'max_y': 5.0,
                'min_z': 0.0, 'max_z': 3.0,
            }],
            output='screen',
        ),
        
        # 6. Voxel Filter
        Node(
            package='pointcloud_filter',
            executable='voxel_grid_filter_node',
            name='voxel_grid',
            parameters=[{
                'voxel_size': 0.05,
            }],
            output='screen',
        ),
        
        # 7. Static Transform
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf',
            arguments=['0', '0', '0', '0', '0', '0', 'camera_link', 'laser']
        ),
    ])