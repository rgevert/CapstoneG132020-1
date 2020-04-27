from parametros import *
from functools import namedtuple

Equipo = namedtuple('Equipo', ['tipo', 'id_', 'proba_falla'])
Kine = namedtuple('Kine', ['nombre', 'id_', 'proba_ausente'])


class Paciente:

    def __init__(self, nombre, patologia):
        self.nombre = nombre
        self.patologia = int(patologia)
        self.cantidad_sesiones = NRO_VISITAS[self.patologia - 1]
        self.sesiones_pendients = self.cantidad_sesiones
        self.sesiones_cumplidas = self.cantidad_sesiones - self.sesiones_pendients
        self.requisito_equipo = USO_EQUIPO_PERSONAL[self.patologia - 1]  # CAMILLA, ULTRASONIDO, INFRARROJO, BICICLETA, CINTA, KINE


    def __repr__(self):
        return (f'{self.nombre}, patologia P{self.patologia}')


class Evento:

    def __init__(self, dia, hora):
        self.dia = dia
        self.hora = hora


class Atencion(Evento):

    def __init__(self, patologia, dia, hora):
        super().__init__(dia, hora)
        self.rango_duracion_sesion = (DURACION_SESION[self.patologia-1] - VAR_DURACION_SESION[self.patologia-1], DURACION_SESION[self.patologia-1] + VAR_DURACION_SESION[self.patologia-1])


class Asignacion:
    pass
