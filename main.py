from sim import CentroKine
from datetime import datetime
from parametros import *



if __name__ == '__main__':
    sim = CentroKine(CANTIDAD_EQUIPO_PERSONAL_DISPONIBLE, datetime(2020,1,1,8), datetime(2020,2,1,8)) # hasta 31/3
    sim.run()
