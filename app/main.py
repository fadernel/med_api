from fastapi import FastAPI, File, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.util import preprocess_image, create_pdf
from pydantic import BaseModel
from fastapi.responses import FileResponse

image_path = '.\\temp\image.jpg'
pdf_path = '.\\temp\\medical_xray_report.pdf'

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class User(BaseModel):
    name: str
    age: str 
    birth: str
    address: str 
    height: str
    weight: str
    disease: str


async def verify_token(request: Request):
    try:
        x_token = request.headers['x-token']
        if x_token != 'LambtonProject':
            raise HTTPException(status_code=403, detail="X-Token header invalid")
    except:
        raise HTTPException(status_code=403, detail="X-Token header invalid")


@app.get("/health", dependencies=[Depends(verify_token)])
async def health():
    return JSONResponse(status_code=200, content={"message": "IT'S ALIVE!!!"})

@app.post("/files", dependencies=[Depends(verify_token)])
async def UploadImage(file: bytes = File(...)):
    #Loading the image
    with open('.\\temp\image.jpg','wb') as image:
        image.write(file)
        image.close()
    return JSONResponse(status_code=200, content={"message": 'image loaded'})

@app.get("/proccessimage", dependencies=[Depends(verify_token)])
async def ProcessImage():
    response = preprocess_image()
    if response is None:
        return JSONResponse(status_code=404, content={"message": 'image not found'})
    else:
        return response
    
@app.post("/createpdf", dependencies=[Depends(verify_token)])
async def CreatePdf(user: User):
    if create_pdf(user.name, user.age, user.birth, user.address, user.height, user.weight, user.disease) == 'created':
        return JSONResponse(status_code=200, content={"message": 'pdf created'})
    return JSONResponse(status_code=500, content={"message": 'error creating the pdf'})

@app.get("/xray_image")
async def image():
    return FileResponse(image_path)

@app.get("/xray_pdf")
async def pdf():
    return FileResponse(pdf_path)

# #Middleware to check credentials
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     try:
#         x_token = request.headers['x-token']
#         if x_token != 'LambtonProject':
#             return JSONResponse(status_code=403, content={})
#         else:
#             response = await call_next(request)
#             return response
#     except:
#         return JSONResponse(status_code=401, content={})
