from sim import CentroKine
from datetime import datetime, timedelta
from parametros import *


if __name__ == '__main__':
    inicio = datetime(2020,1,1,8)
    fin = inicio + timedelta(days = 90)
    alpha = [0 for i in range(9)]
    alpha[1] = 0.2
    sim = CentroKine(inicio, fin, alpha)
    sim.run()
    sim.estadisticas()
