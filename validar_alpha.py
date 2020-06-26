from calcular_alpha import calcular_utilidad, calcular_alfas
import numpy as np
import scipy.stats as st


alfa_0 = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0.3]
var = 0.01
iteraciones_busqueda_alfas = 5
alfa_arbitriario = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0.3]
iteraciones_validacion_alfas = 5


def comparacion_utilidadades(alfa_bueno, alfa_malo, alpha_0, iter_max=30):
    iteracion = 0
    valores_buenos = []
    valores_malos = []
    valores_meh = []
    while iteracion < iter_max:
        bueno = calcular_utilidad(alfa_bueno)
        malo = calcular_utilidad(alfa_malo)
        meh = calcular_utilidad(alpha_0)
        valores_buenos.append(bueno)
        valores_malos.append(malo)
        valores_meh.append(meh)
        iteracion += 1
        print(iter_max-iteracion)
    return st.norm.interval(0.95, loc=np.mean(valores_buenos), scale=st.gstd(valores_buenos)), st.norm.interval(0.95, loc=np.mean(valores_malos), scale=st.gstd(valores_malos)), st.norm.interval(0.95, loc=np.mean(valores_meh), scale=st.gstd(valores_meh)) 


if __name__ == "__main__":
    ut_buena, alfa_bueno, ut_mala, alfa_malo, mejores_utilidades, peores_utilidades, maximos_por_iter = calcular_alfas(alfa_0, var, iteraciones_busqueda_alfas)
    intervalo_bueno, intervalo_malo, intervalo_arbitrario = comparacion_utilidadades(alfa_bueno, alfa_malo, alfa_arbitriario, iteraciones_validacion_alfas)
    print(f'Intervalo con mejor alfa = {alfa_bueno}\n{intervalo_bueno}\nIntervalo con peor alfa = {alfa_malo}\n{intervalo_malo}\nIntervalo con alfa arbitrario = {alfa_arbitriario}\n{intervalo_arbitrario}')