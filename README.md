# mecharm270_pickplace

MechArm 270 로봇암을 이용한 AprilTag 기반 비전 Pick & Place 시스템입니다.
카메라로 AprilTag를 인식하고, 키보드 명령으로 로봇을 제어하여 물체를 집어 지정 위치에 놓습니다.

---

## 패키지 구성

| 패키지 | 역할 |
|--------|------|
| `my_mecharm_interfaces` | 커스텀 ROS2 메시지 및 액션 인터페이스 정의 |
| `mecharm_vision_pick` | 카메라 인식, 로봇 제어 서버, 키보드 조작 노드 |

---

## my_mecharm_interfaces

### 개요
`mecharm_vision_pick`에서 사용하는 커스텀 ROS2 인터페이스(메시지, 액션)를 정의하는 패키지입니다.

### 인터페이스 정의

#### 메시지 (msg/)

**`Tag.msg`** — 단일 AprilTag 정보
```
int32 id          # 태그 ID
float64[6] pose   # [x, y, z, roll, pitch, yaw] (단위: m, deg)
```

**`TagArray.msg`** — 감지된 태그 목록
```
Tag[] tags        # Tag 메시지 배열
```

#### 액션 (action/)

**`RobotCommand.action`** — 로봇 명령 액션
```
# Goal
string command    # "ready" | "pick" | "place"
int32 tag_id      # pick 시 대상 태그 ID

# Result
bool success      # 명령 성공 여부

# Feedback
string status     # 현재 동작 상태 문자열
```

### 빌드
```bash
cd ~/cobot_ws
colcon build --packages-select my_mecharm_interfaces
source install/setup.bash
```

---

## mecharm_vision_pick

### 개요
AprilTag 비전 인식과 로봇 Pick & Place 동작을 통합하는 패키지입니다.
세 개의 노드로 구성됩니다.

### 노드 구성

#### `camera_node`
- USB 카메라(device 0)로 영상을 캡처합니다.
- `pupil_apriltags` 라이브러리로 `tag36h11` 계열 AprilTag를 실시간 감지합니다.
- 각 태그의 3D 위치(x, y, z)와 자세(roll, pitch, yaw)를 추정합니다.
- 감지 결과를 `detected_tags` 토픽(`TagArray`)으로 퍼블리시합니다.
- 태그 크기 기본값: **2.5 cm**

#### `robot_action_server` (실행 이름: `robot_server`)
- `robot_command` 액션 서버를 제공합니다.
- `detected_tags` 토픽을 구독해 현재 감지된 태그 정보를 유지합니다.
- 카메라 좌표 → 로봇 좌표 변환 후 MechArm 270(`/dev/ttyACM0`, 115200bps)을 직접 제어합니다.

지원 명령:

| 명령 | 동작 |
|------|------|
| `ready` | 준비 자세로 이동 |
| `pick` | 지정 tag_id의 물체를 집음 |
| `place` | 현재 물체를 지정 위치에 내려놓음 |

#### `keyboard_node`
- 터미널 키 입력으로 `robot_command` 액션 클라이언트를 통해 로봇에 명령을 전송합니다.

| 키 | 명령 |
|----|------|
| `t` | ready |
| `c` | pick (tag ID 추가 입력) |
| `z` | place |

### 의존성

**Python 라이브러리**
```bash
pip install pupil-apriltags opencv-python pymycobot
```

**ROS2 패키지**
- `rclpy`, `std_msgs`, `action_msgs`, `my_mecharm_interfaces`

---

## 빌드 및 실행

### 1. 빌드
```bash
cd ~/cobot_ws
colcon build --packages-select my_mecharm_interfaces mecharm_vision_pick
source install/setup.bash
```

### 2. 카메라 + 로봇 서버 실행 (launch)
```bash
ros2 launch mecharm_vision_pick mecharm_system.launch.py
```

### 3. 키보드 노드 실행 (별도 터미널)
```bash
source ~/cobot_ws/install/setup.bash
ros2 run mecharm_vision_pick keyboard_node
```

### 4. 동작 순서
```
1. launch 파일 실행 → camera_node, robot_server 자동 시작
2. keyboard_node 실행
3. t  → 로봇 준비 자세 이동
4. c  → tag ID 입력 후 해당 물체 Pick
5. z  → Place 위치에 물체 내려놓기
```

---

## 토픽 및 액션 구조

```
camera_node
    └─[pub]─▶ /detected_tags (TagArray)
                    └─[sub]─▶ robot_action_server

keyboard_node
    └─[action client]─▶ /robot_command (RobotCommand)
                              └─[action server]─▶ robot_action_server
```

---

## 주의사항

- 로봇 연결 포트 기본값: `/dev/ttyACM0` — 환경에 따라 `robot_action_server.py` 내 포트를 수정하세요.
- 카메라 좌표 → 로봇 좌표 변환 계수는 캘리브레이션 환경에 맞게 조정이 필요할 수 있습니다.
- AprilTag 실물 크기가 2.5 cm가 아닌 경우 `camera_node.py`의 `self.tag_size` 값을 수정하세요.
- 키보드 노드는 launch 파일에서 주석 처리되어 있으므로 **별도 터미널에서 수동 실행**해야 합니다.
