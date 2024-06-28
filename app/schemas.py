from pydantic import BaseModel
from typing import Optional # en caso de que algun dato sea opcional

class EstadoBase(BaseModel):
    nombre: str

class EstadoCreate(EstadoBase):
    pass

class Estado(EstadoBase):
    id: int

    class Config:
        orm_mode = True

class MunicipioBase(BaseModel):
    nombre: str
    id_estado: int

class MunicipioCreate(MunicipioBase):
    pass

class Municipio(MunicipioBase):
    id: int

    class Config:
        orm_mode = True

class CandidatoBase(BaseModel):
    nombre: str
    edad: int
    licencia_conduccion: str
    fecha_expiracion: str
    direccion: str
    telefono: str
    email: str
    experiencia: str
    id_municipio: int
    id_estado: int

class CandidatoCreate(CandidatoBase):
    pass

class Candidato(CandidatoBase):
    id: int

    class Config:
        orm_mode = True

class AutomovilBase(BaseModel):
    year: int
    modelo: str
    engomado: str
    id_candidato: int

class AutomovilCreate(AutomovilBase):
    pass

class Automovil(AutomovilBase):
    id: int

    class Config:
        orm_mode = True

class ChatBase(BaseModel):
    id: int
    conversacion: str
    id_candidato: int

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: int

    class Config:
        orm_mode = True