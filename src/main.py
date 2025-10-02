"""FastAPI application entry point."""

import logging

from fastapi import FastAPI

from .routers import documents

logger = logging.getLogger("uvicorn")

app = FastAPI()

app.include_router(documents.router)


@app.get("/")
async def root():
    """Health check endpoint.
    
    Returns:
        A simple hello world message confirming the API is running.
    """
    return {"message": "Hello World"}
