from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pyfastic.api import crud
from pyfastic.dependencies import templates
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse
from pyfastic.dependencies import templates
from sqlalchemy.ext.asyncio import AsyncSession
from pyfastic.database import get_db
from pyfastic.api.crud import get_all_loras
from pyfastic.api.crud import create_lora

router = APIRouter(
    prefix="/loras",
    tags=["loras"]
)
@router.get("/", response_class=HTMLResponse)
async def list_loras(request: Request, db: AsyncSession = Depends(get_db)):
    loras = await get_all_loras(db)
    
    return templates.TemplateResponse(
        request=request,
        name="loras/index.html",
        context={
            "loras": loras
        }
    )

@router.post("/add", response_class=HTMLResponse)
async def add_lora(
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    scale: float = Form(...),
    trigger: str | None = Form(None)
):
    await create_lora(db, name=name, scale=scale, trigger=trigger)
    return RedirectResponse(url="/loras", status_code=303)

    