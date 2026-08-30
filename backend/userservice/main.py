import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import py_eureka_client.eureka_client as eureka_client

# --- Eureka Registration Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register with Eureka on Startup
    await eureka_client.init_async( # type: ignore
        eureka_server=os.getenv("EUREKA_SERVER_URL", "http://eureka-server:8761/eureka"),
        app_name="user-service",
        instance_port=8070 # CHANGED: Match the docker-compose Uvicorn port
    )

    yield
    
    # Gracefully unregister on Shutdown
    await eureka_client.stop_async()

# --- 1. Database Connection Configuration ---
DATABASE_URL = os.getenv(
    "DB_URL", 
    "postgresql://postgres:postgres@localhost:5432/userdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. Database Models (Separate Tables) ---

class AdminOfficial(Base):
    __tablename__ = "officials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phno = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    agency = Column(String, nullable=False)
    state_code = Column(String, nullable=False)
    district_codes = Column(Text, nullable=False)  # Comma-separated: "HAFLONG,CACHAR"
    h3_res6_cells = Column(Text, nullable=False)   # Comma-separated: "8642a42e7ffffff,8642a42f7ffffff"

class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phno = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, default="USER")
    h3_home_cell = Column(String, index=True, nullable=False) # e.g. "8642a42e7ffffff"
    preferred_language = Column(String, default="English", nullable=False)

Base.metadata.create_all(bind=engine)

# --- 3. Pydantic Request/Response Schemas ---

# Ingestion Schemas (Auth-Service -> UserService)
class AdminIngestDTO(BaseModel):
    name: str
    email: str
    phno: str
    password: str
    role: str
    designation: str
    employee_id: str
    agency: str
    state_code: str
    district_codes: str
    h3_res6_cells: str

class CitizenIngestDTO(BaseModel):
    name: Optional[str] = "Citizen"
    phno: str
    email: Optional[str] = None
    password: str
    role: str = "USER"
    h3_home_cell: str
    preferred_language: str = "English"

# Alert Response Schemas (UserService -> Notification-Service)
class AdminNotificationTarget(BaseModel):
    name: str
    email: str
    phno: str
    designation: str
    agency: str
    role: str

    class Config:
        from_attributes = True

class CitizenNotificationTarget(BaseModel):
    name: Optional[str]
    phno: str
    h3_home_cell: str
    preferred_language: str

    class Config:
        from_attributes = True

# --- 4. FastAPI Setup & Dependency ---
app = FastAPI(
    title="TerraSentry User Repository Service",
    description="Internal Database Ingestion and Alert Query Service (Create & Read Only)",
    lifespan=lifespan
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================================
# --- 5. INGESTION ENDPOINTS (Fired by Auth-Service on Register) ---
# =====================================================================

@app.post("/api/v1/sync/admin", status_code=status.HTTP_201_CREATED)
def ingest_admin(payload: AdminIngestDTO, db: Session = Depends(get_db)):
    admin = AdminOfficial(**payload.model_dump())
    try:
        db.add(admin)
        db.commit()
        return {"status": "SUCCESS", "message": "Admin profile recorded"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Official with this email or employee ID already exists"
        )

@app.post("/api/v1/sync/citizen", status_code=status.HTTP_201_CREATED)
def ingest_citizen(payload: CitizenIngestDTO, db: Session = Depends(get_db)):
    citizen = Citizen(**payload.model_dump())
    try:
        db.add(citizen)
        db.commit()
        return {"status": "SUCCESS", "message": "Citizen profile recorded"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Citizen with this phone number already exists"
        )

# =====================================================================
# --- 6. ALERT TARGET ENDPOINTS (Consumed by Notification-Service) ---
# =====================================================================

@app.get(
    "/api/v1/alerts/citizens/h3/{h3_cell}", 
    response_model=List[CitizenNotificationTarget]
)
def get_citizens_by_h3(h3_cell: str, db: Session = Depends(get_db)):
    """
    Returns all citizens whose primary location is in the affected H3 cell.
    Includes preferred language so notifications can be localized (e.g., Assamese, Bengali, Hindi).
    """
    citizens = db.query(Citizen).filter(Citizen.h3_home_cell == h3_cell).all()
    return citizens

@app.get(
    "/api/v1/alerts/admins/h3/{h3_cell}", 
    response_model=List[AdminNotificationTarget]
)
def get_admins_by_h3(h3_cell: str, db: Session = Depends(get_db)):
    """
    Returns all officials/disaster managers overseeing jurisdiction containing the affected H3 cell.
    """
    admins = db.query(AdminOfficial).filter(
        AdminOfficial.h3_res6_cells.like(f"%{h3_cell}%")
    ).all()
    return admins

@app.get(
    "/api/v1/alerts/admins/district/{district_code}", 
    response_model=List[AdminNotificationTarget]
)
def get_admins_by_district(district_code: str, db: Session = Depends(get_db)):
    """
    Returns all officials assigned to a wider district for escalation notices.
    """
    admins = db.query(AdminOfficial).filter(
        AdminOfficial.district_codes.like(f"%{district_code.upper()}%")
    ).all()
    return admins