import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from my_mecharm_interfaces.action import RobotCommand
from my_mecharm_interfaces.msg import Tag, TagArray
# from std_msgs.msg import Float64MultiArray

from pymycobot import MechArm270
import time


class RobotActionServer(Node):

    def __init__(self):

        super().__init__('robot_action_server')

        self.server = ActionServer(
            self,
            RobotCommand,
            'robot_command',
            self.execute_callback
            
        )
        
        self.get_logger().info("Robot Action Server started")

        self.mc = MechArm270('/dev/ttyACM0',115200)

        self.ready_pos = [0,0,-30,0,100,0]
        self.robot_speed = 30
        
        self.tag_sub = self.create_subscription(
            TagArray,
            'detected_tags',
            self.tag_callback,
            10
        )
        self.detected_tags: dict[int, list[float]] = {}
        
    def tag_callback(self, msg):
        self.detected_tags.clear()
        for tag in msg.tags:
            self.detected_tags[tag.id] = tag.pose
            
    def pose_to_coord_xy(self, px, py):
        coord_x = 165.36 * px - 722.66 * py + 240.53
        coord_y = -676.80 * px - 221.30 * py + 15.30
        return coord_x, coord_y

    async def execute_callback(self, goal_handle):
        cmd = goal_handle.request.command
        tag_id = goal_handle.request.tag_id

        self.get_logger().info(f"Execute command={cmd}, tag_id={tag_id}")

        feedback = RobotCommand.Feedback()

        try:

            if cmd == "ready":

                feedback.status = "moving_to_ready"
                goal_handle.publish_feedback(feedback)
                self.get_logger().info("Moving to ready position")

                self.mc.send_angles(self.ready_pos, self.robot_speed)
                time.sleep(2)

            elif cmd == "pick":

                feedback.status = "checking_tag"
                goal_handle.publish_feedback(feedback)

                if tag_id not in self.detected_tags:
                    self.get_logger().warn(f"Tag {tag_id} not found")

                    result = RobotCommand.Result()
                    result.success = False

                    goal_handle.abort()
                    return result
                tag_pose = self.detected_tags[tag_id]
                px, py = tag_pose[0], tag_pose[1]

                self.get_logger().info(f"Tag {tag_id} pose = {tag_pose}")

                feedback.status = "opening_gripper"
                goal_handle.publish_feedback(feedback)

                self.mc.init_gripper()
                time.sleep(0.1)

                self.mc.set_gripper_value(100, 50, 1)
                time.sleep(1)

                feedback.status = "moving_above_tag"
                goal_handle.publish_feedback(feedback)

                coord_x, coord_y = self.pose_to_coord_xy(px, py)

                self.get_logger().info(f"target coord = ({coord_x:.1f}, {coord_y:.1f})")

                self.mc.send_coords([coord_x, coord_y, 140, 179.9, 3.33, 176.75], self.robot_speed)
                time.sleep(2)

                feedback.status = "descending"
                goal_handle.publish_feedback(feedback)

                self.mc.send_coords([coord_x, coord_y, 110, 179.9, 3.33, 176.75], self.robot_speed)
                time.sleep(2)

                feedback.status = "grasping"
                goal_handle.publish_feedback(feedback)

                self.mc.set_gripper_value(0, 50, 1)
                time.sleep(2)
                
                if self.mc.get_gripper_value() <= 10:
                    self.get_logger().info(f"Gripper value: {self.mc.get_gripper_value()}")
                    self.get_logger().warn("No grip detected")

                feedback.status = "returning_ready"
                goal_handle.publish_feedback(feedback)

                self.mc.send_angles(self.ready_pos, self.robot_speed)
                time.sleep(2)

            elif cmd == "place":

                feedback.status = "moving_to_place"
                goal_handle.publish_feedback(feedback)

                self.mc.send_angles([0, 50, -35, 0, 70, 0], self.robot_speed)
                time.sleep(2)

                feedback.status = "release_object"
                goal_handle.publish_feedback(feedback)

                self.mc.set_gripper_value(100, 50, 1)
                time.sleep(2)

                feedback.status = "returning_ready"
                goal_handle.publish_feedback(feedback)
                self.mc.send_angles(self.ready_pos, self.robot_speed)
                time.sleep(2)

            goal_handle.succeed()

            result = RobotCommand.Result()
            result.success = True

            self.get_logger().info(f"{cmd} completed successfully")

            return result

        except Exception as e:

            self.get_logger().error(f"Robot command failed: {str(e)}")

            result = RobotCommand.Result()
            result.success = False

            goal_handle.abort()

            return result


def main():

    rclpy.init()

    node = RobotActionServer()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()