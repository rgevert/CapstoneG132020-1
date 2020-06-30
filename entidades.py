from datetime import datetime, timedelta
from random import uniform, normalvariate, choice, randint, random, shuffle, seed as rseed
from itertools import count
from numpy.random import poisson, seed as nseed

from parametros import *


#nseed(0)

class Paciente:

    n = count(start = 0)

    def __init__(self, patologia):

        self.id = next(self.n)
        self.patologia = patologia

        self.cantidad_sesiones = NRO_VISITAS[patologia - 1]
        self.sesiones_asignadas = 0
        self.sesiones_cumplidas = []
        self.sesiones_atendidas = 0

        self.sesiones_cumplidas_externas = 0

        self.recursos_necesitados = USO_EQUIPO_PERSONAL[patologia - 1]

        self.ultima_sesion_asignada = None
        self.ultima_sesion_cumplida = None

        tiempo_min = MIN_HORAS_ENTRE_VISITAS[patologia - 1]
        tiempo_max = MAX_HORAS_ENTRE_VISITAS[patologia - 1]
        self.tiempo_min = timedelta(hours = tiempo_min)
        self.tiempo_max = timedelta(hours = tiempo_max)

        duracion_sesion = DURACION_SESION[patologia - 1]
        self.duracion_sesion = timedelta(minutes = duracion_sesion*60)

        self.penalidad = PENALIDAD_SESION_FUERA_DE_PLAZO[patologia - 1]

    def ausente(self):
        proba = random()
        proba = 0.2
        if len(self.sesiones_cumplidas) < 5:
            return proba < AUSENTISMO_HASTA_5
        elif len(self.sesiones_cumplidas) <= 13:
            return proba < AUSENTISMO_5_A_13
        else:
            return proba < AUSENTISMO_DESDE_14

class Evento:
    n = count(start = 0)

    def __init__(self, hora_inicio, hora_fin, recursos_necesitados = None):
        self.inicio = hora_inicio
        self.final = hora_fin
        self.final_original = hora_fin
        self.pasadas = 0

        self.cumplido = False
        self.id = next(self.n)

        self.fallo = False

        if recursos_necesitados is None:
            self.recursos_necesitados = [0, 0, 0, 0, 0, 0]
        else:
            self.recursos_necesitados = recursos_necesitados


class Atencion(Evento):

    def __init__(self, paciente, hora_inicio, hora_fin, seed):
        super().__init__(hora_inicio, hora_fin, paciente.recursos_necesitados)
        self.paciente = paciente
        self.seed = seed
        


    #retorna el numero del equipo que falla y la hora
    def falla(self):
        rec = [i for i in range(6)]
        shuffle(rec)

        while rec:
            equipo = rec.pop(0)
            if self.recursos_necesitados[equipo] > 0:
                if equipo < 5 and random() < PROBA_FALLA_EQUIPO:
                    hora_fin = self.inicio + timedelta(hours = 6)
                    recursos = [0,0,0,0,0,0]
                    recursos[equipo] = 1
                    self.fallo = True
                    return Falla(self.inicio, hora_fin, recursos)

                elif equipo == 5 and random() < PROBA_AUSENTISMO:
                    hora_fin = self.inicio + timedelta(hours = 6)
                    recursos = [0,0,0,0,0,1]
                    self.fallo = True
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

    def __init__(self, hora_inicio, seed):
        super().__init__(hora_inicio, hora_inicio, None)
        self.seed = seed

    def lista_pacientes(self):
        #return [Paciente(3) for i in range(1)]
        rseed(self.seed)
        cantidad_pacientes = [int(uniform(0, 4.75)), int(uniform(0, 4)), int(uniform(0.45, 4.34)),
                              int(uniform(0, 2.89)), int(uniform(0, 5)), int(uniform(0.35, 4.44)),
                              int(uniform(0, 5.28)), int(uniform(0, 4.24)), int(uniform(0, 4.12))]
        lista_pacientes = []
        for i, cant in enumerate(cantidad_pacientes):
            for _ in range(cant):
                lista_pacientes.append(Paciente(i+1))
        return lista_pacientes

class Falla(Evento):
    
    def __init__(self, hora_inicio, hora_fin, recursos_necesitados):
        super().__init__(hora_inicio, hora_fin, recursos_necesitados)