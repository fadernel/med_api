from fastapi import FastAPI, File, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.util import preprocess_image, create_pdf, upload_image
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uvicorn

image_path = '.\\temp\image.jpg'
pdf_path = '.\\temp\\medical_xray_report.pdf'

origins = [
    "http://localhost",
    "http://localhost:8080",
]

tags_metadata = [
    {
        "name": "health",
        "description": "Method to check if the api is working, it doesn't require a token.",
    },
    {
        "name": "files",
        "description": "Method to upload images, it requires a token.",
    },
    {
        "name": "proccessimage",
        "description": "Method to proccess the image using the ML Model, it requires a token.",
    },
    {
        "name": "createpdf",
        "description": "Method to create a PDF report, it requires a token.",
    },
    {
        "name": "xray_image",
        "description": "Method to get the image stored in the server, it doesn't require a token.",
    },
    {
        "name": "xray_pdf",
        "description": "Method to get the pdf stored in the server, it doesn't require a token.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/health", dependencies=[Depends(verify_token)], tags=["health"])
async def health():
    return JSONResponse(status_code=200, content={"message": "IT'S ALIVE!!!"})

@app.post("/files", dependencies=[Depends(verify_token)], tags=["files"])
async def UploadImage(file: bytes = File(...)):
    upload_image(file)
    return JSONResponse(status_code=200, content={"message": 'image loaded'})

@app.get("/proccessimage", dependencies=[Depends(verify_token)], tags=["proccessimage"])
async def ProcessImage():
    response = preprocess_image()
    if response is None:
        return JSONResponse(status_code=404, content={"message": 'image not found'})
    else:
        return response
    
@app.post("/createpdf", dependencies=[Depends(verify_token)], tags=["createpdf"])
async def CreatePdf(user: User):
    if create_pdf(user.name, user.age, user.birth, user.address, user.height, user.weight, user.disease) == 'created':
        return JSONResponse(status_code=200, content={"message": 'pdf created'})
    return JSONResponse(status_code=500, content={"message": 'error creating the pdf'})

@app.get("/xray_image", tags=["xray_image"])
async def image():
    return FileResponse(image_path)

@app.get("/xray_pdf", tags=["xray_pdf"])
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