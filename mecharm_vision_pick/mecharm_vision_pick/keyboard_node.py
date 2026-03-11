import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from my_mecharm_interfaces.action import RobotCommand

import threading


class KeyboardNode(Node):

    def __init__(self):
        super().__init__('keyboard_node')

        self.client = ActionClient(
            self,
            RobotCommand,
            'robot_command'
        )

        # 키보드 입력 스레드 시작
        thread = threading.Thread(target=self.keyboard_loop)
        thread.daemon = True
        thread.start()

    def send(self, cmd, tag_id=0):

        goal = RobotCommand.Goal()
        goal.command = cmd
        goal.tag_id = tag_id

        self.client.wait_for_server()

        self.client.send_goal_async(goal)

        self.get_logger().info(f"send {cmd}, tag_id={tag_id}")

    def keyboard_loop(self):

        while rclpy.ok():

            key = input("command (c:pick, z:place, t:ready) : ")

            if key == "c":

                try:
                    tag_id = int(input("pick 할 tag id 입력: "))
                    self.send("pick", tag_id)

                except ValueError:
                    self.get_logger().warn("숫자를 입력해야 합니다.")

            elif key == "z":
                self.send("place")

            elif key == "t":
                self.send("ready")

            else:
                print("unknown command")


def main():

    rclpy.init()

    node = KeyboardNode()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == "__main__":
    main()