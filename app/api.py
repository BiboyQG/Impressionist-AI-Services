from fastapi import APIRouter, HTTPException, Body, status
from fastapi.responses import JSONResponse

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}
