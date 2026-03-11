from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # keyboard_arg = DeclareLaunchArgument(
    #     'keyboard',
    #     default_value='true'
    # )

    # keyboard_node = Node(
    #     package='mecharm_vision_pick',
    #     executable='keyboard_node',
    #     name='keyboard_node',
    #     condition=IfCondition(LaunchConfiguration('keyboard'))
    # )

    camera_node = Node(
        package='mecharm_vision_pick',
        executable='camera_node',
        name='camera_node'
    )

    robot_server = Node(
        package='mecharm_vision_pick',
        executable='robot_server',
        name='robot_server'
    )

    return LaunchDescription([
        # keyboard_arg,
        # keyboard_node,
        camera_node,
        robot_server,
    ])