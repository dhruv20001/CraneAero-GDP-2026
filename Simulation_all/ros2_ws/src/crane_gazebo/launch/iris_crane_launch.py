"""
iris_crane_launch.py
Launch file ROS2 pour iris_crane avec Gazebo Harmonic + ArduPilot

Usage :
  ros2 launch iris_crane_description iris_crane_launch.py
"""

import os
from ament_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('iris_crane_description')
    pkg_ardupilot_gz = get_package_share_directory('ardupilot_gazebo')

    # -------------------------------------------------------
    # 1. Gazebo Harmonic avec le monde par défaut
    # -------------------------------------------------------
    gz_sim = ExecuteProcess(
        cmd=[
            'gz', 'sim', '-r',
            os.path.join(pkg_ardupilot_gz, 'worlds', 'iris_runway.sdf')
        ],
        output='screen'
    )

    # -------------------------------------------------------
    # 2. Spawn du modèle iris_crane (URDF/xacro → SDF via gz)
    # -------------------------------------------------------
    xacro_file = os.path.join(pkg, 'urdf', 'iris_crane.xacro')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description':
                ExecuteProcess(
                    cmd=['xacro', xacro_file],
                    output='screen'
                )
        }]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'iris_crane',
            '-file', xacro_file,
            '-x', '0', '-y', '0', '-z', '0.5'
        ],
        output='screen'
    )

    # -------------------------------------------------------
    # 3. ROS2 <-> Gazebo Bridge (tous les topics capteurs)
    # -------------------------------------------------------
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros2_bridge',
        output='screen',
        parameters=[{
            'config_file': os.path.join(pkg, 'config', 'ros2_gz_bridge.yaml'),
            'expand_gz_topic_names': True,
        }]
    )

    # -------------------------------------------------------
    # 4. depth_image_proc : génère les PointCloud2 depuis Depth
    #    (si le plugin Gazebo ne le fait pas nativement)
    # -------------------------------------------------------
    pc2_front = Node(
        package='depth_image_proc',
        executable='point_cloud_xyzrgb_node',
        name='pc2_front',
        remappings=[
            ('rgb/image_rect_color',     '/camera_front/color/image_raw'),
            ('rgb/camera_info',           '/camera_front/color/camera_info'),
            ('depth_registered/image_rect', '/camera_front/depth/image_rect_raw'),
            ('points',                    '/camera_front/depth/points'),
        ]
    )

    pc2_down = Node(
        package='depth_image_proc',
        executable='point_cloud_xyzrgb_node',
        name='pc2_down',
        remappings=[
            ('rgb/image_rect_color',     '/camera_down/color/image_raw'),
            ('rgb/camera_info',           '/camera_down/color/camera_info'),
            ('depth_registered/image_rect', '/camera_down/depth/image_rect_raw'),
            ('points',                    '/camera_down/depth/points'),
        ]
    )

    # -------------------------------------------------------
    # 5. ArduPilot SITL (optionnel - lance en arrière plan)
    #    Décommentez si vous voulez lancer SITL depuis le launch
    # -------------------------------------------------------
    # ardupilot_sitl = ExecuteProcess(
    #     cmd=[
    #         'arducopter',
    #         '--model', 'gazebo-iris',
    #         '--speedup', '1',
    #         '--defaults', os.path.join(pkg_ardupilot_gz, 'config', 'iris.parm'),
    #     ],
    #     output='screen'
    # )

    return LaunchDescription([
        gz_sim,
        TimerAction(period=3.0, actions=[spawn_entity]),
        TimerAction(period=4.0, actions=[bridge]),
        TimerAction(period=4.0, actions=[pc2_front]),
        TimerAction(period=4.0, actions=[pc2_down]),
    ])
