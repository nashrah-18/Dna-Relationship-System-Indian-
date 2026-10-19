from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, HospitalLog, PoliceLog, PoliceCase
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

@router.get("/dashboard", response_class=HTMLResponse)
def government_dashboard(request: Request):
    try:
        user_id, sector = get_current_user(request)
        if sector != "government":
            raise HTTPException(status_code=403)
        html = render_template("government_dashboard.html", request=request, user_id=user_id)
        return HTMLResponse(content=html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<pre>{traceback.format_exc()}</pre>", status_code=500)

@router.get("/hospital-activity", response_class=HTMLResponse)
def hospital_activity(request: Request, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "government":
        raise HTTPException(status_code=403)
    now = datetime.datetime.utcnow()
    two_days_ago = now - datetime.timedelta(days=2)
    two_min_ago = now - datetime.timedelta(minutes=2)
    hospital_adds = db.query(HospitalLog).filter(HospitalLog.action == "add", HospitalLog.timestamp >= two_days_ago).count()
    hospital_ids = [u[0] for u in db.query(HospitalLog.user_id).filter(HospitalLog.action == "add", HospitalLog.timestamp >= two_days_ago).distinct().all()]
    hospital_updates = db.query(HospitalLog).filter(HospitalLog.action == "delete", HospitalLog.timestamp >= two_min_ago).count()
    html = render_template("government_activity.html",
                           request=request, user_id=user_id, sector="hospital",
                           hospital_adds=hospital_adds,
                           hospital_ids=", ".join(hospital_ids) if hospital_ids else "None",
                           hospital_updates=hospital_updates)
    return HTMLResponse(content=html)

@router.get("/police-activity", response_class=HTMLResponse)
def police_activity(request: Request, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "government":
        raise HTTPException(status_code=403)
    now = datetime.datetime.utcnow()
    two_days_ago = now - datetime.timedelta(days=2)
    twenty_days_ago = now - datetime.timedelta(days=20)
    police_adds = db.query(PoliceLog).filter(PoliceLog.action == "add_case", PoliceLog.timestamp >= two_days_ago).count()
    solved_cases = db.query(PoliceCase).filter(PoliceCase.status == "Solved", PoliceCase.timestamp >= twenty_days_ago).count()
    solved_ids = [c[0] for c in db.query(PoliceCase.case_id).filter(PoliceCase.status == "Solved", PoliceCase.timestamp >= twenty_days_ago).all()]
    html = render_template("government_activity.html",
                           request=request, user_id=user_id, sector="police",
                           police_adds=police_adds,
                           solved_cases=solved_cases,
                           solved_case_ids=", ".join(solved_ids) if solved_ids else "None")
    return HTMLResponse(content=html)