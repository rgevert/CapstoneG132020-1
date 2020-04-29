from datetime import datetime, timedelta
from random import uniform, normalvariate, choice, randint
from itertools import count

from parametros import *


class Paciente:

    n = count(start = 0)

    def __init__(self, patologia):

        self.id = next(self.n)
        self.patologia = patologia

        self.cantidad_sesiones = NRO_VISITAS[patologia - 1]
        self.sesiones_asignadas = 0
        self.sesiones_cumplidas = 0

        self.recursos_necesitados = USO_EQUIPO_PERSONAL[patologia - 1]

        self.hora_ultima_sesion_asignada = None
        self.hora_ultima_sesion_cumplida = None

        tiempo_min = MIN_HORAS_ENTRE_VISITAS[patologia - 1]
        tiempo_max = MAX_HORAS_ENTRE_VISITAS[patologia - 1]
        self.tiempo_min = timedelta(hours = tiempo_min)
        self.tiempo_max = timedelta(hours = tiempo_max)

        duracion_sesion = DURACION_SESION[patologia - 1]
        self.duracion_sesion = timedelta(minutes = duracion_sesion*60)


class Evento:

    def __init__(self, hora_inicio, hora_fin, recursos_necesitados):
        self.inicio = hora_inicio
        self.final = hora_fin

        self.cumplido = False

        if recursos_necesitados is None:
            self.recursos_necesitados = [0, 0, 0, 0, 0, 0]
        else:
            self.recursos_necesitados = recursos_necesitados


class Atencion(Evento):

    def __init__(self, paciente, hora_inicio, hora_fin):
        super().__init__(hora_inicio, hora_fin, paciente.recursos_necesitados)
        self.paciente = paciente

class AtencionExterna(Evento):

    def __init__(self, paciente, hora_inicio, hora_fin):
        super().__init__(hora_inicio, hora_fin, None)
        self.paciente = paciente

class AsignacionSemanal(Evento):

    def __init__(self, hora_inicio):
        super().__init__(hora_inicio, hora_inicio, None)

    def lista_pacientes(self):

        return [Paciente(1) for _ in range(10)]




