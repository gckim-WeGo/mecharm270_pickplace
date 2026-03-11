import rclpy
from rclpy.node import Node
from my_mecharm_interfaces.msg import Tag, TagArray
# from std_msgs.msg import Float64MultiArray

import cv2
import numpy as np
from pupil_apriltags import Detector
    
class CameraNode(Node):

    def __init__(self):
        super().__init__('camera_node')

        self.pub = self.create_publisher(
            TagArray,
            'detected_tags',
            10
        )

        self.cap = cv2.VideoCapture(0)
        ret, _init_frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to access camera")
        _init_frame = cv2.rotate(_init_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        h, w = _init_frame.shape[:2]
        frame_center = (w / 2, h / 2)

        fx = fy = w
        cx, cy = w / 2, h / 2
        self.camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float64)
        self.camera_params = (fx, fy, cx, cy)
        self.tag_size = 0.025
        
        self.detector = Detector(
            families="tag36h11",
            nthreads=2,
            quad_decimate=2.0,
            quad_sigma=0.8,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0
        )

        self.timer = self.create_timer(0.03, self.loop)

    def loop(self):

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        tags = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.camera_params,
            tag_size=self.tag_size
        )
        
        detected_tags: dict[int, list[float]] = {}
        # detected_tags = []
        
        msg = TagArray()
        # msg = Float64MultiArray()

        for tag in tags:
            corners = tag.corners
            center = tag.center
            R = tag.pose_R
            t = tag.pose_t

            for point in corners:
                cv2.circle(frame, (int(point[0]), int(point[1])), 4, (0, 0, 255), -1)

            rvec, _ = cv2.Rodrigues(R)
            tvec = t.reshape(3, 1)
            cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, self.tag_size / 2)

            pos_x, pos_y, pos_z = tvec[0][0], tvec[1][0], tvec[2][0]
            euler_angles = cv2.RQDecomp3x3(R)[0]
            center_x, center_y = int(center[0]), int(center[1])
            
            cv2.putText(frame, f"ID: {tag.tag_id}", (center_x, center_y - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(frame, f"Pos: ({pos_x:.2f}, {pos_y:.2f}, {pos_z:.2f})m",
                        (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(frame, f"Rot: ({euler_angles[0]:.1f}, {euler_angles[1]:.1f}, {euler_angles[2]:.1f})deg",
                        (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            detected_tags[tag.tag_id] = [pos_x, pos_y, pos_z, euler_angles[0], euler_angles[1], euler_angles[2]]
            
            # detected_tags.append([tag.tag_id, pos_x, pos_y, pos_z, euler_angles[0], euler_angles[1], euler_angles[2]])

        self.get_logger().info(f"Detected : {detected_tags}")
        
        for tid, pose in detected_tags.items():
            t = Tag()
            t.id = tid
            t.pose = pose
            msg.tags.append(t)
        
        self.pub.publish(msg)


def main():

    rclpy.init()

    node = CameraNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()