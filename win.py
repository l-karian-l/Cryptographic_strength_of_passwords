from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from hashlib import sha256 
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5 import uic
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class Window1(QtWidgets.QDialog):
    def __init__(self):
        super(Window1, self).__init__()
        uic.loadUi('Win1.ui', self)

        self.max_workers = 0
        self.length = 5  # Длина пароля
        self.sB_streams.setMaximum(os.cpu_count())
        self.sB_streams.setMinimum(1)

        self.lE_hash2.setReadOnly(True)
        self.pB_tb.setEnabled(False)
        
        self.pB_tb.clicked.connect(lambda: self.all_file(self.lE_hash2))
        self.cB_from_the_file.stateChanged.connect(self.from_the_file) # Check box 1"Выбрать все"

        self.cB_1.stateChanged.connect(self.single_threaded)
        self.cB_many.stateChanged.connect(self.multi_threading)

        self.pB_run.stateChanged.connect(self.run)

    # Выбор файла
    def all_file(self, line_edit):
        pathfile, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if pathfile:  # Проверяем, что файл выбран
            line_edit.setText(pathfile)

    # Работа для чек бокса "Вывести из файла"
    def from_the_file(self, state):
        if state == Qt.Checked:  # Если чекбокс включен
            self.lE_hash.setReadOnly(True)
            self.pB_tb.setEnabled(True)
        else:  # Если чекбокс выключен
            self.lE_hash2.clear()  # Очищаем поле
            self.lE_hash.setReadOnly(False)
            self.pB_tb.setEnabled(False)

    # Работа для чек бокса "Однопоточный"
    def single_threaded(self, state):
        if state == Qt.Checked:
            self.cB_many.setEnabled(False)
            self.max_workers = 1
        else:
            self.cB_many.setEnabled(True)

    # Работа для чек бокса "Многопоточный"
    def multi_threading(self, state):
        if state == Qt.Checked:
            self.cB_1.setEnabled(False)
            self.max_workers = self.sB_streams.value()
        else:
            self.cB_1.setEnabled(True)

    #Запуск фун-ии
    #def run(self):
        


        
        

         

if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        Login = Window1()
        Login.show()
        sys.exit(app.exec_())