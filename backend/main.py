from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from .detector import detector
import io
import base64
from PIL import Image

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost:5173", # React 개발 서버
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트 (빌드된 React 앱을 서빙할 때 사용 예정, 현재는 개발 모드라 필요 없을 수 있음)
# app.mount("/static", StaticFiles(directory="frontend"), name="static") 

@app.post("/detect")
async def detect_people(file: UploadFile = File(...)):
    try:
        # 이미지 읽기
        contents = await file.read()
        
        # 사람 감지
        boxes, img = detector.predict(contents)
        person_count = len(boxes)
        found = person_count > 0
        
        message = f"{person_count}명의 사람이 감지되었습니다." if found else "사람을 찾을 수 없습니다."
        
        response_data = {
            "found": found,
            "count": person_count,
            "message": message
        }
        
        if found:
            # 박스 그리기
            result_image_bytes = detector.visualize(img, boxes)
            # Base64 인코딩
            encoded_image = base64.b64encode(result_image_bytes).decode('utf-8')
            response_data["image"] = f"data:image/jpeg;base64,{encoded_image}"
            
        return JSONResponse(content=response_data)
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
def read_root():
    return {"message": "사람 인식 API가 실행 중입니다."}
