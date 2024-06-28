from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/estados", response_model=List[schemas.Estado])
def read_estados(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    estados = db.query(models.Estado).offset(skip).limit(limit).all()
    return estados

@router.post("/estados", response_model=schemas.Estado)
def create_estado(estado: schemas.EstadoCreate, db: Session = Depends(get_db)):
    db_estado = models.Estado(**estado.model_dump())
    db.add(db_estado)
    db.commit()
    db.refresh(db_estado)
    return db_estado

@router.get("/estados/{estado_id}", response_model=schemas.Estado)
def read_estado(estado_id: int, db: Session = Depends(get_db)):
    db_estado = db.query(models.Estado).filter(models.Estado.id == estado_id).first()
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return db_estado

@router.put("/estados/{estado_id}", response_model=schemas.Estado)
def update_estado(estado_id: int, estado: schemas.EstadoCreate, db: Session = Depends(get_db)):
    db_estado = db.query(models.Estado).filter(models.Estado.id == estado_id).first()
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    for key, value in estado.model_dump().items():
        setattr(db_estado, key, value)
    db.add(db_estado)
    db.commit()
    db.refresh(db_estado)
    return db_estado

@router.delete("/estados/{estado_id}", response_model=schemas.Estado)
def delete_estado(estado_id: int, db: Session = Depends(get_db)):
    db_estado = db.query(models.Estado).filter(models.Estado.id == estado_id).first()
    if db_estado is None:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    db.delete(db_estado)
    db.commit()
    return db_estado

# Definir rutas similares para municipios, candidatos, automóviles, chats (proyectos en segunda fase)
