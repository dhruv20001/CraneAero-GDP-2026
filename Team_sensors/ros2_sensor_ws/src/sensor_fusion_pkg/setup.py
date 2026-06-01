from setuptools import setup
from glob import glob
import os

package_name = 'sensor_fusion_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
     data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dhruv',
    maintainer_email='dhruv@todo.todo',
    description='Sensor fusion package',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fusion = sensor_fusion_pkg.fusion:main',
            'lidar_to_pointcloud = sensor_fusion_pkg.lidar_to_pointcloud:main',
            'time_sync_monitor = sensor_fusion_pkg.time_sync_monitor:main',
            'voxel_filter = sensor_fusion_pkg.voxel_filter:main',
        ],
    },
)