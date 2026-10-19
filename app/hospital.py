from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, DNAProfile, HospitalLog
from app.auth import get_current_user
from app.templating import render_template
import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_action(db, user_id, action, sample_id=None):
    log = HospitalLog(user_id=user_id, action=action, sample_id=sample_id, timestamp=datetime.datetime.utcnow())
    db.add(log)
    db.commit()

@router.get("/dashboard", response_class=HTMLResponse)
def hospital_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, sector = get_current_user(request)
        if sector != "hospital":
            raise HTTPException(status_code=403)
        msg = request.query_params.get("msg")
        html = render_template("hospital_dashboard.html", request=request, user_id=user_id, msg=msg)
        return HTMLResponse(content=html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<pre>{traceback.format_exc()}</pre>", status_code=500)

@router.get("/add-data", response_class=HTMLResponse)
def add_data_page(request: Request):
    user_id, sector = get_current_user(request)
    if sector != "hospital":
        raise HTTPException(status_code=403)
    html = render_template("hospital_add.html", request=request, user_id=user_id)
    return HTMLResponse(content=html)

@router.get("/check-database", response_class=HTMLResponse)
def check_database_page(request: Request, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "hospital":
        raise HTTPException(status_code=403)
    profiles = db.query(DNAProfile).all()
    html = render_template("hospital_check.html", request=request, profiles=profiles, user_id=user_id)
    return HTMLResponse(content=html)

@router.post("/add")
def add_record(request: Request, db: Session = Depends(get_db),
               sample_id: str = Form(...), sex: str = Form(...),
               amel: int = Form(0), d3s1358: int = Form(0), vwa: int = Form(0),
               d16s539: int = Form(0), csf1po: int = Form(0), tpox: int = Form(0),
               d8s1179: int = Form(0), d21s11: int = Form(0), d18s51: int = Form(0),
               dys391: int = Form(0), d2s441: int = Form(0), d19s433: int = Form(0),
               tho1: int = Form(0), fga: int = Form(0), d22s1045: int = Form(0),
               d5s818: int = Form(0), d13s317: int = Form(0), d7s820: int = Form(0),
               se33: int = Form(0), d10s1248: int = Form(0), d1s1656: int = Form(0),
               d12s391: float = Form(0.0), d2s1338: int = Form(0)):
    user_id, sector = get_current_user(request)
    if sector != "hospital":
        raise HTTPException(status_code=403)
    if db.query(DNAProfile).filter(DNAProfile.sample_id == sample_id).first():
        return RedirectResponse(url="/hospital/dashboard?msg=Sample+ID+exists", status_code=303)
    new_profile = DNAProfile(
        sample_id=sample_id, sex=sex, amel=amel, d3s1358=d3s1358, vwa=vwa,
        d16s539=d16s539, csf1po=csf1po, tpox=tpox, d8s1179=d8s1179, d21s11=d21s11,
        d18s51=d18s51, dys391=dys391, d2s441=d2s441, d19s433=d19s433, tho1=tho1,
        fga=fga, d22s1045=d22s1045, d5s818=d5s818, d13s317=d13s317, d7s820=d7s820,
        se33=se33, d10s1248=d10s1248, d1s1656=d1s1656, d12s391=d12s391, d2s1338=d2s1338
    )
    db.add(new_profile)
    db.commit()
    log_action(db, user_id, "add", sample_id)
    return RedirectResponse(url="/hospital/dashboard?msg=Database+updated.", status_code=303)

@router.post("/delete/{sample_id}")
def delete_record(request: Request, sample_id: str, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "hospital":
        raise HTTPException(status_code=403)
    profile = db.query(DNAProfile).filter(DNAProfile.sample_id == sample_id).first()
    if not profile:
        raise HTTPException(status_code=404)
    db.delete(profile)
    db.commit()
    log_action(db, user_id, "delete", sample_id)
    return RedirectResponse(url="/hospital/dashboard?msg=Database+updated.", status_code=303)