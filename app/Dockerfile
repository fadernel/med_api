FROM python:3.10-slim

RUN python -m pip install reportlab
RUN python -m pip install pillow
RUN python -m pip install torch
RUN python -m pip install torchvision
RUN python -m pip install fastapi
RUN python -m pip install pydantic
RUN python -m pip install uvicorn
RUN python -m pip install python-multipart


WORKDIR /code
COPY . .

USER 1001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
