from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'mecharm_vision_pick'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ('share/' + package_name + '/action', ['action/RobotCommand.action']),
        # ('share/' + package_name + '/msg', ['msg/Tag.msg']),
        # ('share/' + package_name + '/msg', ['msg/TagArray.msg']),
        (os.path.join('share', package_name, 'msg'), glob('msg/*.msg')),
        (os.path.join('share', package_name, 'action'), glob('action/*.action')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='wego',
    maintainer_email='gc.kim@wego-robotics.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_node = mecharm_vision_pick.camera_node:main',
            'robot_server = mecharm_vision_pick.robot_action_server:main',
            'keyboard_node = mecharm_vision_pick.keyboard_node:main',
        ],
    },
)
