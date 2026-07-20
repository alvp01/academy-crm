from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.classroom import router as classroom_router
from app.api.headquarters import router as headquarters_router

app = FastAPI(title="Academy CRM", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(headquarters_router)
app.include_router(classroom_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
