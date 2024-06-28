from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Estado(Base):
    __tablename__ = "estados"
    id_estado = Column(Integer, primary_key=True, index=True)
    nombre_estado = Column(String(255), nullable=False)
    disponibilidad_estado = Column(Boolean, nullable=False)

    municipios = relationship("Municipio", back_populates="estado")
    candidatos = relationship("Candidato", back_populates="estado")

class Municipio(Base):
    __tablename__ = "municipios"
    id_municipio = Column(Integer, primary_key=True, index=True)
    nombre_municipio = Column(String(255), nullable=False)
    id_estado_fk = Column(Integer, ForeignKey("estados.id_estado"))

    estado = relationship("Estado", back_populates="municipios")
    candidatos = relationship("Candidato", back_populates="municipio")

class Candidato(Base):
    __tablename__ = "candidatos"
    id_candidato = Column(Integer, primary_key=True, index=True)
    nombre_candidato = Column(String(255), nullable=False)
    edad_candidato = Column(Integer, nullable=False)
    licencia_conduccion = Column(String(255), nullable=False)
    fecha_expiracion_licencia = Column(Date, nullable=False)
    direccion_candidato = Column(String(255), nullable=False)
    telefono_candidato = Column(String(20), nullable=False)
    email_candidato = Column(String(255), nullable=False)
    experiencia_candidato = Column(String(255), nullable=False)
    disponibilidad_candidato = Column(Boolean, nullable=False)
    id_municipio_fk = Column(Integer, ForeignKey("municipios.id_municipio"))
    id_estado_fk = Column(Integer, ForeignKey("estados.id_estado"))

    municipio = relationship("Municipio", back_populates="candidatos")
    estado = relationship("Estado", back_populates="candidatos")
    automoviles = relationship("Automovil", back_populates="candidato")
    chats = relationship("Chat", back_populates="candidato")

class Automovil(Base):
    __tablename__ = "automoviles"
    id_auto = Column(Integer, primary_key=True, index=True)
    year_auto = Column(Integer, nullable=False)
    modelo_auto = Column(String(255), nullable=False)
    engomado_auto = Column(String(255), nullable=False)
    id_candidato_fk = Column(Integer, ForeignKey("candidatos.id_candidato"))

    candidato = relationship("Candidato", back_populates="automoviles")

class Chat(Base):
    __tablename__ = "chats"
    id_chat = Column(Integer, primary_key=True, index=True)
    conversacion_reclutamiento = Column(String(), nullable=False)
    id_candidato_fk = Column(Integer, ForeignKey("candidatos.id_candidato"))

    candidato = relationship("Candidato", back_populates="chats")
