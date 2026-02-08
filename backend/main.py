from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from .detector import detector
import io
import base64
from PIL import Image

app = FastAPI()

# 1. CORS 설정 (Cross-Origin Resource Sharing)
# React 프론트엔드(보통 5173 포트)에서 백엔드(8000 포트)로 요청을 보낼 때,
# 보안상의 이유로 브라우저가 차단하는 것을 막기 위해 허용할 도메인을 설정합니다.
origins = [
    "http://localhost:5173", # React 개발 서버 주소
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 허용할 출처 목록
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"], # 모든 헤더 허용
)

# 2. 이미지 업로드 및 감지 API 엔드포인트
# POST 요청으로 '/detect' 경로에 파일이 업로드되면 이 함수가 실행됩니다.
@app.post("/detect")
async def detect_people(file: UploadFile = File(...)):
    try:
        # 업로드된 파일의 내용을 바이트 단위로 읽습니다.
        contents = await file.read()
        
        # detector.py의 predict 함수를 호출하여 사람을 찾습니다.
        # return: boxes(위치 좌표 리스트), img(원본 이미지 객체)
        boxes, img = detector.predict(contents)
        person_count = len(boxes) # 찾은 사람 수
        found = person_count > 0 # 발견 여부 (True/False)
        
        # 결과 메시지 생성
        message = f"{person_count}명의 사람이 감지되었습니다." if found else "사람을 찾을 수 없습니다."
        
        # 프론트엔드로 보낼 응답 데이터 구성
        response_data = {
            "found": found,
            "count": person_count,
            "message": message
        }
        
        if found:
            # 사람이 있다면, 이미지에 초록색 박스를 그립니다.
            result_image_bytes = detector.visualize(img, boxes)
            # 이미지를 웹으로 전송하기 위해 Base64 문자열로 인코딩합니다.
            encoded_image = base64.b64encode(result_image_bytes).decode('utf-8')
            # HTML img 태그에서 바로 사용할 수 있는 포맷으로 변환합니다.
            response_data["image"] = f"data:image/jpeg;base64,{encoded_image}"
            
        return JSONResponse(content=response_data)
        
    except Exception as e:
        # 에러 발생 시 500 상태 코드와 함께 에러 메시지를 반환합니다.
        return JSONResponse(content={"error": str(e)}, status_code=500)

# 3. 기본 경로 확인용 엔드포인트
@app.get("/")
def read_root():
    return {"message": "사람 인식 API가 실행 중입니다."}
