from datetime import datetime, timedelta
from random import uniform, normalvariate, choice, randint, random
from itertools import count
from numpy.random import poisson

from parametros import *


class Paciente:

    n = count(start = 0)

    def __init__(self, patologia):

        self.id = next(self.n)
        self.patologia = patologia

        self.cantidad_sesiones = NRO_VISITAS[patologia - 1]
        self.sesiones_asignadas = 0
        self.sesiones_cumplidas = 0
        self.sesiones_atendidas = 0

        self.sesiones_cumplidas_externas = 0

        self.recursos_necesitados = USO_EQUIPO_PERSONAL[patologia - 1]

        self.hora_ultima_sesion_asignada = None
        self.hora_ultima_sesion_cumplida = None

        tiempo_min = MIN_HORAS_ENTRE_VISITAS[patologia - 1]
        tiempo_max = MAX_HORAS_ENTRE_VISITAS[patologia - 1]
        self.tiempo_min = timedelta(hours = tiempo_min)
        self.tiempo_max = timedelta(hours = tiempo_max)

        duracion_sesion = DURACION_SESION[patologia - 1]
        self.duracion_sesion = timedelta(minutes = duracion_sesion*60)

        self.penalidad = PENALIDAD_SESION_FUERA_DE_PLAZO[patologia - 1]


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

    def ausente(self):
        if self.paciente.sesiones_cumplidas < 5:
            return random() < AUSENTISMO_HASTA_5
        elif self.paciente.sesiones_cumplidas <= 13:
            return random() < AUSENTISMO_5_A_13
        else:
            return random() < AUSENTISMO_DESDE_14

    #retorna el numero del equipo que falla y la hora
    def falla(self):

        if random() < PROBA_AUSENTISMO:
            hora_fin = self.inicio + timedelta(hours = 6)
            recursos = [0,0,0,0,0,1]
            return Falla(self.inicio, hora_fin, recursos)

        for equipo, cantidad in enumerate(self.recursos_necesitados[:5]):
            if cantidad > 0:
                if random() < PROBA_FALLA_EQUIPO:
                    hora_fin = self.inicio + timedelta(hours = 6)
                    recursos = [0,0,0,0,0,0]
                    recursos[equipo] = 1
                    return Falla(self.inicio, hora_fin, recursos)

        return False



    def actualizar_duracion(self):
        variacion = VAR_DURACION_SESION[self.paciente.patologia - 1]
        duracion = DURACION_SESION[self.paciente.patologia - 1]*(1-variacion/2)*60*60
        duracion += random()*variacion*60*60
        duracion = int(duracion)
        self.final = self.inicio + timedelta(seconds = duracion)


class AtencionExterna(Evento):

    def __init__(self, paciente, hora_inicio, hora_fin):
        super().__init__(hora_inicio, hora_fin, None)
        self.paciente = paciente

class AsignacionSemanal(Evento):

    def __init__(self, hora_inicio):
        super().__init__(hora_inicio, hora_inicio, None)

    def lista_pacientes(self):
        lista_pacientes = []
        for i in range(9):
            for j in range(poisson(TASA_LLEGADA_SEMANAL[i])):
                lista_pacientes.append(Paciente(i+1))
        return lista_pacientes

class Falla(Evento):
    
    def __init__(self, hora_inicio, hora_fin, recursos_necesitados):
        super().__init__(hora_inicio, hora_fin, recursos_necesitados)
