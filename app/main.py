from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, leads, pipeline
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="WapNexus Lead Generation",
    description="Scrape local businesses, classify with an LLM, and generate outreach drafts.",
    version="1.0.0",
    lifespan=lifespan,
    servers=[{"url": "https://lead-api.wapnexus.com", "description": "Production"}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(pipeline.router)
app.include_router(leads.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
