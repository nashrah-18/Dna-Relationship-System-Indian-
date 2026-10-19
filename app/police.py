from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, DNAProfile, HospitalLog, PoliceCase, PoliceLog
from app.auth import get_current_user
from app.ai_model import get_relationship
from app.templating import render_template
import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def log_police_action(db, user_id, action, case_id):
    log = PoliceLog(user_id=user_id, action=action, case_id=case_id, timestamp=datetime.datetime.utcnow())
    db.add(log)
    db.commit()

@router.get("/dashboard", response_class=HTMLResponse)
def police_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user_id, sector = get_current_user(request)
        if sector != "police":
            raise HTTPException(status_code=403)
        total_profiles = db.query(DNAProfile).count()
        last_log = db.query(HospitalLog).order_by(HospitalLog.timestamp.desc()).first()
        last_update = last_log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_log else "Never"
        html = render_template("police_dashboard.html",
                               request=request, user_id=user_id,
                               last_update=last_update, total_profiles=total_profiles)
        return HTMLResponse(content=html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<pre>{traceback.format_exc()}</pre>", status_code=500)

@router.get("/relationship", response_class=HTMLResponse)
def relationship_page(request: Request):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    html = render_template("police_relationship.html", request=request, user_id=user_id)
    return HTMLResponse(content=html)

@router.post("/relationship/search")
def search_relationships(request: Request, sample_id: str = Form(...), db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    target = db.query(DNAProfile).filter(DNAProfile.sample_id == sample_id).first()
    if not target:
        return {"error": "Sample ID not found"}
    all_profiles = db.query(DNAProfile).filter(DNAProfile.sample_id != sample_id).all()
    results = []
    for p in all_profiles:
        rel, conf, perc = get_relationship(target, p)
        results.append({"sample_id": p.sample_id, "percentage": perc, "relationship": rel, "confidence": conf})
    results.sort(key=lambda x: x["percentage"], reverse=True)
    return {"results": results[:7]}

@router.post("/relationship/compare")
def compare_two(request: Request, id1: str = Form(...), id2: str = Form(...), db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    p1 = db.query(DNAProfile).filter(DNAProfile.sample_id == id1).first()
    p2 = db.query(DNAProfile).filter(DNAProfile.sample_id == id2).first()
    if not p1 or not p2:
        return {"error": "One or both IDs not found"}
    rel, conf, perc = get_relationship(p1, p2)
    return {"percentage": perc, "relationship": rel, "confidence": conf}

@router.get("/cases", response_class=HTMLResponse)
def cases_page(request: Request, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    all_cases = db.query(PoliceCase).order_by(PoliceCase.timestamp.desc()).all()
    msg = request.query_params.get("msg")
    html = render_template("police_cases.html", request=request, cases=all_cases, user_id=user_id, msg=msg)
    return HTMLResponse(content=html)

@router.post("/cases/add")
def add_case(request: Request, case_id: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    if db.query(PoliceCase).filter(PoliceCase.case_id == case_id).first():
        return RedirectResponse(url="/police/cases?msg=Case+ID+exists", status_code=303)
    new_case = PoliceCase(case_id=case_id, description=description, status="Unsolved", updated_by=user_id, timestamp=datetime.datetime.utcnow())
    db.add(new_case)
    db.commit()
    log_police_action(db, user_id, "add_case", case_id)
    return RedirectResponse(url="/police/cases?msg=Case+added", status_code=303)

@router.post("/cases/solve/{case_id}")
def solve_case(request: Request, case_id: str, db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    case = db.query(PoliceCase).filter(PoliceCase.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404)
    case.status = "Solved"
    case.updated_by = user_id
    case.timestamp = datetime.datetime.utcnow()
    db.commit()
    log_police_action(db, user_id, "solve_case", case_id)
    return RedirectResponse(url="/police/cases?msg=Database+updated.", status_code=303)

@router.post("/cases/search")
def search_case(request: Request, search_id: str = Form(...), db: Session = Depends(get_db)):
    user_id, sector = get_current_user(request)
    if sector != "police":
        raise HTTPException(status_code=403)
    case = db.query(PoliceCase).filter(PoliceCase.case_id == search_id).first()
    if not case:
        return {"error": "Case not found"}
    return {"case_id": case.case_id, "description": case.description, "status": case.status}