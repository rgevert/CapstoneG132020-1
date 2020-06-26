import matplotlib.pyplot as plt
from sim import CentroKine
from datetime import datetime, timedelta
from random import randint


def calcular_utilidad(alpha):
    paso = True
    while paso:
        try:
            inicio = datetime(2020,1,1,8)
            fin = inicio + timedelta(days = 90)
            sim = CentroKine(inicio, fin, alpha)
            sim.run()
            ut = sim.estadisticas()
            paso = False
        except:
            pass
    return ut


def nuevo_alpha(alpha, var):

    primero = randint(0, 8)
    segundo = randint(0, 8)

    alfa = alpha.copy()

    if primero == segundo:
        while primero == segundo:
            segundo = randint(0, 8)
    if alfa[segundo] >= var or alfa[primero] >= 1 - var:
        alfa[primero] += var
        alfa[segundo] -= var
    else:
        nuevo_alpha(alfa, var)
    return alfa


def calcular_alfas(alfa_0, var=0.01, iter_max=1000):
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

    incumbent_ut = calcular_utilidad(alfa_0)
    incumbent_alfa = alfa_0
    nova_ut = [(incumbent_ut, incumbent_alfa)]
    mala_ut = incumbent_ut
    mal_alfa = incumbent_alfa
    malas_utilidades = [(mala_ut, mal_alfa)]
    maximos_por_iter = [incumbent_ut]
    iteracion = 0
    while iteracion < iter_max:
        alfas = [nuevo_alpha(incumbent_alfa, var) for _ in range(5)]
        utilidades = [calcular_utilidad(alpha) for alpha in alfas]
        mejor_utilidad = max(utilidades)
        mejor_alfa = alfas[utilidades.index(mejor_utilidad)]
        peor_utilidad = min(utilidades)
        peor_alfa = alfas[utilidades.index(peor_utilidad)]
        maximos_por_iter.append(mejor_utilidad)
        if peor_utilidad < mala_ut:
            mala_ut = peor_utilidad
            mal_alfa = peor_alfa
            malas_utilidades.append((mala_ut, mal_alfa))
        if mejor_utilidad > incumbent_ut:
            incumbent_ut = mejor_utilidad
            incumbent_alfa = mejor_alfa
            nova_ut.append((incumbent_ut, incumbent_alfa))
        iteracion += 1
        # print(iter_max - iteracion)
    return incumbent_ut, incumbent_alfa, mala_ut, mal_alfa, nova_ut, malas_utilidades, maximos_por_iter


if __name__ == '__main__':
    ut, alfa, ut_c, alfa_c, utilidad, anti_utilidad, maximos = calcular_alfas([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0.3], iter_max=10)
    utilidades = [i[0] for i in utilidad]
    alfas_buenos = [i[1] for i in utilidad]
    anti_utilidades = [i[0] for i in anti_utilidad]
    alfas_malos = [i[1] for i in anti_utilidad]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(utilidades)
    ax2.plot(anti_utilidades)
    plt.show()
