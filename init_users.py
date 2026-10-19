import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal, User, Base, engine
from app.auth import hash_password

print("Initializing database...")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

session = SessionLocal()

users_data = [
    ("H01", "hospital", "HDna001"),
    ("H02", "hospital", "HDna002"),
    ("H03", "hospital", "HDna003"),
    ("H04", "hospital", "HDna004"),
    ("H05", "hospital", "HDna005"),
    ("P01", "police", "PDna001"),
    ("P02", "police", "PDna002"),
    ("P03", "police", "PDna003"),
    ("P04", "police", "PDna004"),
    ("P05", "police", "PDna005"),
    ("G01", "government", "GDna001"),
    ("G02", "government", "GDna002"),
    ("G03", "government", "GDna003"),
    ("G04", "government", "GDna004"),
    ("G05", "government", "GDna005"),
]

for uid, sector, pwd in users_data:
    user = User(id=uid, sector=sector, password_hash=hash_password(pwd))
    session.add(user)

session.commit()
session.close()

print(f"Inserted {len(users_data)} users.")
print("Database ready!")