from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="Image Sentiment and Contextual Analysis API",
    description="Upload an image to detect human emotion and background objects.",
    version="1.0"
)

app.include_router(router)
