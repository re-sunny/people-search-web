import sys
import os

try:
    print("Testing imports...")
    import torch
    import torchvision
    import cv2
    import numpy as np
    from PIL import Image
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    print("Testing model load...")
    weights = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=weights)
    model.eval()
    print("Model loaded successfully.")
    
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)

print("Verification passed!")
