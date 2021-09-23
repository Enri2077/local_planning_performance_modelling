# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is all-in-one launch script intended for use by nav2 developers."""

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    # Get the launch directory
    bringup_dir = get_package_share_directory('local_planning_performance_modelling')
    launch_dir = os.path.join(bringup_dir, 'launch')

    return LaunchDescription([

        DeclareLaunchArgument('params_file', description='Full path to the ROS2 parameters file to use for all launched nodes'),
        DeclareLaunchArgument('rviz_config_file', description='Full path to the RVIZ config file to use'),
        DeclareLaunchArgument('headless', description='Whether to execute gzclient)'),

        DeclareLaunchArgument('world', description='Full path to world model file to load'),
        DeclareLaunchArgument('gazebo_model_path_env_var', description='GAZEBO_MODEL_PATH environment variable'),
        DeclareLaunchArgument('gazebo_plugin_path_env_var', description='GAZEBO_PLUGIN_PATH environment variable'),

        SetEnvironmentVariable('GAZEBO_MODEL_PATH', LaunchConfiguration('gazebo_model_path_env_var')),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH', LaunchConfiguration('gazebo_plugin_path_env_var')),
        ExecuteProcess(cmd=['gzserver', '-s', 'libgazebo_ros_init.so', LaunchConfiguration('world'), '--verbose', '-s', 'libgazebo_ros_factory.so'], cwd=[launch_dir], output='screen'),
        ExecuteProcess(cmd=['gzclient'], condition=IfCondition(PythonExpression(['not ', LaunchConfiguration('headless')])), cwd=[launch_dir], output='screen'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[LaunchConfiguration('urdf')]),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(launch_dir, 'rviz.launch.py')),
            # condition=IfCondition(PythonExpression(['not ', headless])),  # TODO uncomment before running on server
            launch_arguments={'rviz_config_file': LaunchConfiguration('rviz_config_file')}.items()),

    ])