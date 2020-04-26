from parametros import *
from functools import namedtuple

Equipo = namedtuple('Equipo', ['tipo'])
Kine = namedtuple('Kine', ['Nombre'])

class Persona:

    def __init__(self, nombre, patologia):
        self.nombre = nombre
        self.patologia = int(patologia)
        self.cantidad_sesiones = NRO_VISITAS[self.patologia - 1]
        self.sesiones_pendients = self.cantidad_sesiones
        self.sesiones_cumplidas = self.cantidad_sesiones - self.sesiones_pendients
        self.rango_duracion_sesion = (DURACION_SESION[self.patologia-1] - VAR_DURACION_SESION[self.patologia-1], DURACION_SESION[self.patologia-1] + VAR_DURACION_SESION[self.patologia-1])

    def __repr__(self):
        return (f'{self.nombre}, patologia P{self.patologia}')


class Equipo:

    def __init__(self, tipo, identificador):
        self.id_ = identificador
        self.tipo = tipo
