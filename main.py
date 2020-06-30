from ventanas import VentanaInicio, VentanaResultados, VentanaSimulando
from validar_alpha import Validar
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":

    def hook(type, value, traceback):
        print(type)
        print(traceback)
    sys.__excepthook__ = hook

    a = QApplication(sys.argv)
    ventana_inicio = VentanaInicio()
    ventana_simulando = VentanaSimulando()
    ventana_res = VentanaResultados()
    validar = Validar()

    ventana_inicio.senal_sim.connect(validar.set_parametros)
    validar.senal_terminar.connect(ventana_res.mostrar)

    ventana_inicio.show()
    sys.exit(a.exec())
