from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # 2. Intel RealSense Camera
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='camera',
            parameters=[{
                'enable_depth': True,
                'enable_pointcloud': True,
                'pointcloud.enable': True,
                'decimation_filter.enable': True,
                'decimation_filter.filter_magnitude': 8,
                'depth_module.profile': '640x480x30',
            }],
            output='screen',
        ),
        
        
"""      
        
        # 1. Radar PDK Bridge (runs the radar driver)
        ExecuteProcess(
            cmd=['/opt/pdk/bin/pdk_start.sh'],
            name='pdk_bridge',
            output='screen',
            cwd='/opt/pdk/bin',
        ),
        
        # 3. Camera Pass-through Filter
        Node(
            package='pointcloud_filter',
            executable='camera_passthrough_filter',
            name='camera_passthrough',
            output='screen',
        ),
        
        # 4. Radar Pass-through Filter
        Node(
            package='pointcloud_filter',
            executable='radar_passthrough_filter',
            name='radar_passthrough',
            output='screen',
        ),
        
        # 5. TF Transform: Camera Optical to Camera Link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_camera_optical',
            arguments=['0', '0', '0', '-1.57', '0', '-1.57', 'camera_link', 'camera_depth_optical_frame'],
            output='screen',
        ),
        
        # 6. TF Transform: Radar to Camera Link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_radar',
            arguments=['0', '0', '0', '0', '0', '0', 'camera_link', 'pdk_base_link'],
            output='screen',
        ),
        
        # 7. Fusion Node (Camera + Radar)
        Node(
            package='sensor_fusion_pkg',
            executable='fusion',
            name='fusion',
            output='screen',
        ),
        
        # 8. Voxel Grid Filter (Downsample fused cloud)
        Node(
            package='pointcloud_filter',
            executable='voxel_grid_filter',
            name='voxel_filter',
            parameters=[{'voxel_size': 0.05}],
            output='screen',
        ),
""",
    ])
