from personas import Paciente
from random import uniform, normalvariate, choice
from parametros import *


class Simulation:

    def __init__(self, equipos, dias_totales, metodo, cantidad_equipo):
        self.equipos = equipos
        self.dias_totales = dias_totales
        self.metodo = metodo
        self.dia = 0
        self.hora = 0
        self.eventos = []
        self.cantidad_equipo = cantidad_equipo
        self.pacientes = []
        self.siguiente_evento = None

    def nuevos_pacientes(self):
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
            for i in range(1, n_personas):
                self.pacientes.append(Paciente(choice(NOMBRES), patologia + 1))

    def asignacion_semanal(self):
        for paciente in self.pacientes:
            

    def run(self):
        while self.dia <= 7:
            while self.hora <= DURACION_DIA:
                self.siguiente_evento = self.eventos.pop(0)

            self.dia += 1
