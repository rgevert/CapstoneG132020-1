from functools import reduce
import matplotlib.pyplot as plt
from sim import CentroKine
from datetime import datetime, timedelta



def calcular_utilidad(alpha):
    try:
        inicio = datetime(2020,1,1,8)
        fin = inicio + timedelta(days = 90)
        sim = CentroKine(inicio, fin, alpha)
        sim.run()
        return sim.estadisticas()
    except:
        return calcular_utilidad(alpha)

def calcular_utilidad_promedio(alpha, n_simulaciones):
    suma = 0
    for i in range(n_simulaciones):
        suma += calcular_utilidad(alpha)
    return suma/n_simulaciones

def calcular_alfas(alfa, var_por_iter=0.05):
    c=0
    incumbent_ut = calcular_utilidad(alfa)
    incumbent_alfa = alfa
    print(incumbent_ut)
    nueva_utilidad = incumbent_ut
    nova_ut = [incumbent_ut]
    for elemento, alpha in enumerate(alfa):
        for index, alpha in enumerate(alfa):
            if elemento != index:
                while nueva_utilidad >= incumbent_ut:
                    incumbent_ut = nueva_utilidad
                    incumbent_alfa = alfa
                    if alfa[index] > var_por_iter and alfa[elemento] < 1 - var_por_iter:
                        alfa[elemento] += var_por_iter
                        alfa[index] -= var_por_iter
                    else:
                        break
                    nueva_utilidad = calcular_utilidad_promedio(alfa, 3)
                    nova_ut.append(nueva_utilidad)
                    c += 1
                incumbent_ut = nueva_utilidad
                incumbent_alfa = alfa
        print(incumbent_alfa)
    return incumbent_ut, incumbent_alfa, nova_ut, c


ut, alfa, utilidada, c = calcular_alfas([0.01, 0.02, 0.90, 0.05, 0, 0, 0, 0, 0.2])

print(ut, alfa)
plt.plot(utilidada)
plt.show()