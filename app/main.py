from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.history import router as history_router
from app.api.documents import router as documents_router

from database import create_tables
@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Creating database tables...")
    create_tables()

    yield

    print("Application shutting down...")


app = FastAPI(
    title="DocuMind - A Conversational AI Document Assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(history_router)
app.include_router(documents_router)