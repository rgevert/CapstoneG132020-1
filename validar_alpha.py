import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from random import randint
from sim import CentroKine
from datetime import datetime, timedelta
from dask import delayed
import time


class Validar(QObject):

    senal_actualizar_avance = pyqtSignal(tuple)
    senal_terminar = pyqtSignal(dict)
    senal_partir_simulacion = pyqtSignal(tuple)

    def __init__(self, alfa_0, var, iteraciones_busqueda_alfas, iteraciones_validacion_alfas):
        super().__init__()
        self.alfa_0 = alfa_0
        self.var = var
        self.maximos = []
        self.iteraciones_busqueda_alfas = iteraciones_busqueda_alfas
        self.iteraciones_validacion_alfas = iteraciones_validacion_alfas
        self.intervalo_bueno = None
        self.intervao_malo = None
        self.intervalo_todos = None
        self.confianza_intervalos = 0.95

    def set_parametros(self, parametros):
        self.alfa_0 = parametros[0]
        self.var = parametros[1]
        self.iteraciones_busqueda_alfas = parametros[2]
        self.iteraciones_validacion_alfas = parametros[3]
        self.tipo = parametros[4]
        self.total = self.iteraciones_busqueda_alfas + self.iteraciones_validacion_alfas
        self.senal_partir_simulacion.emit(('CALCULANDO ALFA ÓPTIMO Y PEOR...', self.total))
        self.comparacion_utilidadades()

    def comparacion_utilidadades(self):
        print('CALCULANDO ALFA ÓPTIMO Y PEOR...')
        self.senal_actualizar_avance.emit(('CALCULANDO ALFA ÓPTIMO Y PEOR...', 0))
        self.calcular_alfas()
        print('CALCULANDO INTERVALOS DE CONFIANZA...')
        self.senal_actualizar_avance.emit(('CALCULANDO INTERVALOS DE CONFIANZA...', self.iteraciones_busqueda_alfas))
        iteracion = 0
        valores_buenos = []
        valores_malos = []
        while iteracion < self.iteraciones_validacion_alfas:
            bueno = self.calcular_utilidad(self.alfa_bueno)
            malo = self.calcular_utilidad(self.alfa_malo)
            valores_buenos.append(bueno)
            valores_malos.append(malo)
            iteracion += 1
            print(iteracion)
            self.senal_actualizar_avance.emit(('CALCULANDO INTERVALOS DE CONFIANZA...', iteracion + self.iteraciones_busqueda_alfas))
        self.intervalo_bueno = st.norm.interval(self.confianza_intervalos, loc=np.mean(valores_buenos), scale=st.gstd(valores_buenos))
        self.intervalo_malo = st.norm.interval(self.confianza_intervalos, loc=np.mean(valores_malos), scale=st.gstd(valores_malos))
        self.senal_actualizar_avance.emit(('CALCULANDO INTERVALOS DE CONFIANZA...', iteracion + self.iteraciones_busqueda_alfas))
        self.senal_terminar.emit({'utilidad_buena': self.intervalo_bueno, 'utilidad_mala': self.intervalo_malo, 'todas': self.intervalo_todas_las_ut})

    def calcular_alfas(self):
        '''
        alfa_0: ALFA INICIAL
        var: VARIACION DE CADA ALFA POR ITERACIÓN
        iter_max: CANTIDAD DE ITERACIONES

        RETORNA

        incumbent_ut: MEJOR UTILIDAD
        incumbent_alfa: MEJOR ALFA
        mala_ut: PEOR UTILIDAD
        mal_alfa: PEOR ALFA
        nova_ut: LISTA DE TUPLAS (MEJOR UTILIDAD HASTA EL MOMENTO, MEJOR ALFA HASTA EL MOMENTO)
        malas_utilidades: LISTA DE TUPLAS (PEOR UTILIDAD HASTA EL MOMENTO, PEOR ALFA HASTA EL MOMENTO)
        maximos_por_iter: LISTE DE MEJOR UTILIDAD POR ITERACIÓN
        '''
        
        incumbent_ut = self.calcular_utilidad(self.alfa_0)
        
        incumbent_alfa = self.alfa_0
        nova_ut = [(incumbent_ut, incumbent_alfa)]
        mala_ut = incumbent_ut
        mejor_alfa = incumbent_alfa
        mal_alfa = incumbent_alfa
        malas_utilidades = [(mala_ut, mal_alfa)]
        todas_las_utilidades = [incumbent_ut]
        iteracion = 0
        while iteracion < self.iteraciones_busqueda_alfas:
            
            alfas = [self.nuevo_alpha(mejor_alfa) for _ in range(5)]
            
            utilidades = []
            for alpha in alfas:
                ut = self.calcular_utilidad(alpha)
                utilidades.append(ut)
            mejor_utilidad = max(utilidades)
            mejor_alfa = alfas[utilidades.index(mejor_utilidad)]
            self.maximos.append(mejor_utilidad)
            peor_utilidad = min(utilidades)
            peor_alfa = alfas[utilidades.index(peor_utilidad)]
            todas_las_utilidades += utilidades
            if peor_utilidad < mala_ut:
                mala_ut = peor_utilidad
                mal_alfa = peor_alfa
                malas_utilidades.append((mala_ut, mal_alfa))
            if mejor_utilidad > incumbent_ut:
                incumbent_ut = mejor_utilidad
                incumbent_alfa = mejor_alfa
                nova_ut.append((incumbent_ut, incumbent_alfa))
            iteracion += 1
            print(iteracion)
            self.senal_actualizar_avance.emit(('CALCULANDO ALFA ÓPTIMO Y PEOR...', iteracion))
            self.ut_buena = incumbent_ut
            self.alfa_bueno = incumbent_alfa
            self.ut_mala = mala_ut
            self.alfa_malo = mal_alfa
            self.mejores_utilidades = nova_ut
            self.peores_utilidades = malas_utilidades
            self.intervalo_todas_las_ut = st.norm.interval(self.confianza_intervalos, loc=np.mean(todas_las_utilidades), scale=st.gstd(todas_las_utilidades))

    def calcular_utilidad(self, alpha):
        paso = True
        while paso:
            try:
                inicio = datetime(2020, 1, 1, 8)
                fin = inicio + timedelta(days=90)
                sim = CentroKine(inicio, fin, alpha)
                sim.run()
                ut = sim.estadisticas()
                paso = False
            except:
                pass
        return ut

    def nuevo_alpha(self, alpha):

        primero = randint(0, 8)
        segundo = randint(0, 8)

        alfa = alpha.copy()

        if primero == segundo:
            while primero == segundo:
                segundo = randint(0, 8)
        if alfa[segundo] >= self.var:
            alfa[primero] += self.var
            alfa[segundo] -= self.var
        else:
            self.nuevo_alpha(alfa)
        return alfa


if __name__ == "__main__":
    start = time.time()
    v = Validar([10, 10, 10, 10, 10, 10, 10, 10, 10], 1, 100, 100)
    v.comparacion_utilidadades()
    print(f'AlFA ÓPTIMO = {v.alfa_bueno}, UT = {v.ut_buena}\nALFA MALO = {v.alfa_malo}, UT = {v.ut_mala}')
    print(f'Intervalo con mejor alfa = {v.alfa_bueno}\n{v.intervalo_bueno}\nIntervalo con peor alfa = {v.alfa_malo}\n{v.intervalo_malo}\nIntervalo de todas las utilidades\n{v.intervalo_todas_las_ut}')
    print(f'se demoró {time.time() - start}s')
    plt.plot(v.maximos)
    plt.show()