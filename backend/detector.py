import torch
import torchvision
from torchvision import transforms as T
from PIL import Image
import cv2
import numpy as np
import io

class PersonDetector:
    def __init__(self):
        # 1. Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # 2. Load model
        self.weights = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=self.weights)
        self.model.to(self.device)
        self.model.eval()

        # 3. Transform
        self.transform = T.Compose([T.ToTensor()])

    def predict(self, image_bytes: bytes):
        # Load image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_tensor = self.transform(img).to(self.device)

        # Predict
        with torch.no_grad():
            prediction = self.model([img_tensor])

        # Analyze results
        labels = prediction[0]['labels'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()
        boxes = prediction[0]['boxes'].cpu().numpy()

        person_boxes = []
        for i in range(len(labels)):
            # Label 1 is 'person', score > 0.8
            if labels[i] == 1 and scores[i] > 0.8:
                person_boxes.append(boxes[i].astype(int))

        return person_boxes, img

    def visualize(self, img: Image.Image, boxes: list):
        # Convert PIL to OpenCV format (RGB -> BGR)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        for box in boxes:
            cv2.rectangle(img_cv, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
            cv2.putText(img_cv, "Person", (box[0], box[1]-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert back to RGB for web display compatibility if needed, 
        # or just encode to JPEG for response
        _, buffer = cv2.imencode('.jpg', img_cv)
        return buffer.tobytes()

# Instantiate global detector
detector = PersonDetector()
