# 人物追尾プログラム

## 概要

Gazebo上のロボットカメラ画像から人を検出し、追尾するプログラム。  
ROS 2で画像の受信と移動指令の送信を行う。

## 使用環境

- Ubuntu
- ROS 2 Humble
- Gazebo Classic 11系
- Python 3.10
- NumPy 1.26.4
- Ultralytics 8.4.182（YOLOv8を使用）
- OpenCV、cv_bridge

＊ NumPy 1.26.4とUltralytics 8.4.182の組み合わせで動作確認済み。
```bash
python3 -m pip install numpy==1.26.4 ultralytics==8.4.182
```

## モデルの入手と配置

UltralyticsとOpenCVは、以下コマンドを実施した。

```bash
pip install ultralytics opencv-python
```

`yolov8n.pt` は、[Ultralyticsの学習済みモデル（YOLOv8n）](https://docs.ultralytics.com/models/yolov8/)を使用した。  
`pip install` ではライブラリが入る。  
モデルは初めて読み込むときにダウンロードされるため、あらかじめ取得したい際は以下コマンドを実施する。

```bash
cd ~/pai_ws/src
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

取得したファイルは、以下のようにプログラムと同じ場所に置くこと。  
ディレクトリ・ファイル配置例）
```text
directory name/
├── README.md
└── src/
    ├── chaser_prg.py
    └── yolov8n.pt
```

## 実行手順

### 1. Gazeboを起動する
### 2. 追尾プログラムを起動する
コマンド例）
```bash
source /opt/ros/humble/setup.bash
cd ~/directory name/src
python3 chaser_prg.py
```

## 終了方法

実行中の端末で `Ctrl+C` を実行する。