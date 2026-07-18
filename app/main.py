from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.database.database import Base, engine
from app.database import models  # noqa: F401


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


app = FastAPI(title="Salon AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.include_router(router)
create_tables()


@app.on_event("startup")
def on_startup():
    create_tables()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )
