import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class ObjectTrackerNode(Node):
    def __init__(self):
        super().__init__('object_tracker_node')
        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt') 
        self.get_logger().info('追尾ノード起動')

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        height, width, _ = cv_image.shape
        screen_center_x = width / 2

        # 推論
        results = self.model(cv_image, imgsz=320, stream=True, verbose=False)
        target_detected = False
        twist = Twist()

        for r in results:
            boxes = r.boxes
            for box in boxes:
                # エラーが出ても落ちないようにガード追加
                try:
                    cls_id = int(box.cls[0].item())
                    cls_name = self.model.names[cls_id]
                except Exception:
                    continue
                
                if cls_name == 'person':
                    # エラーが出ても落ちないようにガード追加
                    try:
                        # 座標を変換
                        coords = box.xyxy[0].tolist()
                        x1, y1, x2, y2 = map(int, coords)
                        
                        person_center_x = (x1 + x2) / 2
                        person_width = x2 - x1
                        target_detected = True
                        
                        # 左右の旋回と前進の判定
                        if person_center_x > (screen_center_x + 50):
                            twist.angular.z = -0.2  # 右に回す
                        elif person_center_x < (screen_center_x - 50):
                            twist.angular.z = 0.2   # 左に回す
                        else:
                            twist.angular.z = 0.0
                            if person_width < 150:
                                twist.linear.x = 0.1  # ゆっくり前進
                            else:
                                twist.linear.x = 0.0
                        
                        # 描画エラー対策
                        cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    except Exception as e:
                        # エラーが起きた場合はログ出力する
                        self.get_logger().error(f'計算エラーをスキップしました: {e}')
                        continue
                    break
            if target_detected:
                break

        # 人が見つからないときは安全停止
        if not target_detected:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.publisher_.publish(twist)
        cv2.imshow("YOLOv8 Tracking Viewer", cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
