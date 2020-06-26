import sys
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

qt_name, QtClass = uic.loadUiType('parametros.ui')

class VentanaInicio(qt_name, QtClass):

    senal_sim = pyqtSignal(list)

    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)
        self.sim.clicked.connect(self.simular)
        tipos_simulaciones = ['Vanilla', 'Solo Asignación', 'Solo Alfas', 'Ambas']
        for i in tipos_simulaciones:
            self.tipo_sim.addItem(i)
    
    def simular(self):
        self.hide()
        self.senal_sim.emit([[float(self.alfa1.text()), float(self.alfa2.text()),
                              float(self.alfa3.text()), float(self.alfa4.text()),
                              float(self.alfa5.text()), float(self.alfa6.text()),
                              float(self.alfa7.text()), float(self.alfa8.text()),
                              float(self.alfa9.text())], 
                             float(self.var.text()), int(self.iter_b_alfas.text()),
                             int(self.iter_v_alfas.text()),
                             str(self.tipo_sim.currentText())])
        


qt_name1, QtClass1 = uic.loadUiType('simulando.ui')


class VentanaSimulando(qt_name1, QtClass1):

    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)

    def partir(self, tupla):
        self.total = tupla[1]
        self.avance.setValue(tupla[1])
        self.mensaje.setText(tupla[0])
        self.avance.setValue(0)
        self.show()

    def actualizar(self, tupla):
        self.avance.setValue(tupla[1])
        self.mensaje.setText(tupla[0])
        if self.avance.value() == self.total:
            self.hide()


qt_name2, QtClass2 = uic.loadUiType('resultados.ui')


class VentanaResultados(qt_name2, QtClass2):

    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi(self)

    def mostrar(self, resultados):
        self.inter_bueno.setText(str(resultados['utilidad_buena']))
        self.inter_malo.setText(str(resultados['utilidad_mala']))
        self.inter_todo.setText(str(resultados['todas']))
        self.show()

if __name__ == "__main__":

    def hook(type, value, traceback):
        print(type)
        print(traceback)
    sys.__excepthook__ = hook

    a = QApplication(sys.argv)
    ventana_inicio = VentanaInicio()
    ventana_inicio.show()
    sys.exit(a.exec())
