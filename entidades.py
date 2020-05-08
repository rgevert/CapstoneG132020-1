from datetime import datetime, timedelta
from random import uniform, normalvariate, choice, randint
from itertools import count
from parametros import *


class Paciente:

    n = count(start = 1)

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
    
    def __repr__(self):
        return f'{self.id} P{self.patologia}'


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
    
    def __repr__(self):
        return f'Atencion a paciente {self.paciente}, a las {self.inicio}'


class AtencionExterna(Evento):

    def __init__(self, paciente, hora_inicio, hora_fin):
        super().__init__(hora_inicio, hora_fin, None)
        self.paciente = paciente


class AsignacionSemanal(Evento):

    def __init__(self, hora_inicio):
        super().__init__(hora_inicio, hora_inicio, None)

    def lista_pacientes(self):
        pacientes = []
        proporciones = (uniform(-0.799440823, 6.184056207),
                        uniform(-0.640579676, 5.255964292),
                        uniform(-0.482987409, 6.021448947),
                        uniform(0.019352488, 3.057570589),
                        uniform(0.319904106, 4.910865125),
                        uniform(1.513474791, 4.024986747),
                        uniform(-0.824229691, 5.901152768),
                        uniform(0.091394772, 4.37014369),
                        uniform(-0.27989108, 4.587583388))
        personas = list(map(lambda x: int(x), proporciones))
        for patologia, n_personas in enumerate(personas):
            for _ in range(1, n_personas):
                pacientes.append(Paciente(patologia + 1))
        return pacientes




