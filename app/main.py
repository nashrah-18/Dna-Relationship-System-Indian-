import sys
import traceback
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.auth import authenticate_user, get_current_user
from app.templating import render_template   # <-- only this import
from app.hospital import router as hospital_router
from app.police import router as police_router
from app.government import router as government_router


# ---------- Error Logging Middleware ----------
class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print("=" * 60)
            print("ERROR OCCURRED:")
            traceback.print_exc()
            print("=" * 60)
            raise


# ---------- FastAPI App ----------
app = FastAPI()
app.add_middleware(ErrorLoggingMiddleware)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---------- Database helper ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def sector_select(request: Request):
    try:
        print("🔵 Serving sector_select.html")
        html = render_template("sector_select.html", request=request)
        return HTMLResponse(content=html)
    except Exception as e:
        traceback.print_exc()
        error_html = f"""
        <html>
            <body>
                <h1>Error rendering sector_select.html</h1>
                <pre>{traceback.format_exc()}</pre>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@app.post("/select_sector")
def select_sector(sector: str = Form(...)):
    return RedirectResponse(url=f"/login/{sector}", status_code=303)


@app.get("/login/{sector}", response_class=HTMLResponse)
def login_page(request: Request, sector: str):
    html = render_template("login.html", request=request, sector=sector, error=None)
    return HTMLResponse(content=html)


@app.post("/login/{sector}")
async def login(request: Request, sector: str, db: Session = Depends(get_db)):
    form = await request.form()
    user_id = form.get("user_id")
    password = form.get("password")

    if not user_id or not password:
        html = render_template("login.html", request=request, sector=sector, error="Please fill in all fields")
        return HTMLResponse(content=html, status_code=400)

    if not authenticate_user(db, user_id, password, sector):
        html = render_template("login.html", request=request, sector=sector, error="Invalid credentials")
        return HTMLResponse(content=html, status_code=401)

    response = RedirectResponse(url=f"/dashboard/{sector}", status_code=303)
    response.set_cookie(key="user_id", value=user_id, httponly=True)
    response.set_cookie(key="sector", value=sector, httponly=True)
    return response


@app.get("/dashboard/{sector}")
def dashboard_redirect(request: Request, sector: str):
    user_id, sec = get_current_user(request)
    if sec != sector:
        raise HTTPException(status_code=403, detail="Sector mismatch")
    if sector == "hospital":
        return RedirectResponse(url="/hospital/dashboard", status_code=303)
    elif sector == "police":
        return RedirectResponse(url="/police/dashboard", status_code=303)
    elif sector == "government":
        return RedirectResponse(url="/government/dashboard", status_code=303)
    else:
        raise HTTPException(status_code=404)


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    response.delete_cookie("sector")
    return response


# ---------- Include Routers ----------
app.include_router(hospital_router, prefix="/hospital", tags=["hospital"])
app.include_router(police_router, prefix="/police", tags=["police"])
app.include_router(government_router, prefix="/government", tags=["government"])