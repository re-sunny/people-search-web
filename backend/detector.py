import torch
import torchvision
from torchvision import transforms as T
from PIL import Image
import cv2
import numpy as np
import io

class PersonDetector:
    def __init__(self):
        # 1. 장치 설정 (GPU 사용 가능 확인)
        # CUDA가 있으면 GPU를, 없으면 CPU를 사용합니다.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # 2. 모델 로드
        # 사전 학습된 Faster R-CNN 모델을 불러옵니다. (사람, 자동차 등 일반 사물 인식용)
        self.weights = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=self.weights)
        self.model.to(self.device) # 모델을 메모리(GPU/CPU)에 올립니다.
        self.model.eval() # 평가 모드로 설정 (학습 중지)

        # 3. 이미지 전처리 도구
        self.transform = T.Compose([T.ToTensor()])

    def predict(self, image_bytes: bytes):
        # 바이트 형태의 이미지를 열어서 RGB로 변환합니다.
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # 이미지를 텐서(Tensor)로 변환하고 디바이스로 보냅니다.
        img_tensor = self.transform(img).to(self.device)

        # 예측 실행 (Gradient 계산 비활성화로 메모리 절약)
        with torch.no_grad():
            prediction = self.model([img_tensor])

        # 결과 분석 (GPU에 있는 데이터를 CPU로 가져와서 numpy 배열로 변환)
        labels = prediction[0]['labels'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()
        boxes = prediction[0]['boxes'].cpu().numpy()

        person_boxes = []
        for i in range(len(labels)):
            # Label 1은 'person'(사람)을 의미합니다. 정확도(score)가 0.8(80%) 이상인 것만 선택합니다.
            if labels[i] == 1 and scores[i] > 0.8:
                person_boxes.append(boxes[i].astype(int))

        return person_boxes, img

    def visualize(self, img: Image.Image, boxes: list):
        # PIL 이미지를 OpenCV 포맷(BGR)으로 변환합니다 (OpenCV는 색상 순서가 BGR입니다).
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # 감지된 모든 사람 위치에 박스를 그립니다.
        for box in boxes:
            cv2.rectangle(img_cv, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(img_cv, "Person", (box[0], box[1]-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 웹에서 보여주기 위해 이미지를 JPEG 포맷의 바이트 코드로 변환합니다.
        _, buffer = cv2.imencode('.jpg', img_cv)
        return buffer.tobytes()

# 전체 시스템에서 사용할 탐지기 객체를 하나 생성해둡니다.
detector = PersonDetector()
