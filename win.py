from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from hashlib import sha256 
from string import ascii_lowercase
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5 import uic
import time
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class Window1(QtWidgets.QDialog):
    def __init__(self):
        super(Window1, self).__init__()
        uic.loadUi('Win1.ui', self)

        self.max_workers = 0
        self.length = 5  # Длина пароля
        self.create_info = ""

        self.sB_streams.setMaximum(os.cpu_count())
        self.sB_streams.setMinimum(1)

        self.lE_hash2.setReadOnly(True)
        self.pB_tb.setEnabled(False)
        
        self.pB_tb.clicked.connect(lambda: self.all_file(self.lE_hash2))
        self.cB_from_the_file.stateChanged.connect(self.from_the_file) # Check box 1"Выбрать все"

        self.cB_1.stateChanged.connect(self.single_threaded)
        self.cB_many.stateChanged.connect(self.multi_threading)

        self.pB_run.clicked.connect(self.run)

    # Выбор файла
    def all_file(self, line_edit):
        try:
            pathfile, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
            if pathfile:  # Проверяем, что файл выбран
                line_edit.setText(pathfile)
        except Exception as e:
            self.show_error(f"Ошибка при выборе файла: {e}") 

    # Работа для чек бокса "Вывести из файла"
    def from_the_file(self, state):
        if state == Qt.Checked:  # Если чекбокс включен
            self.lE_hash.setReadOnly(True)
            self.pB_tb.setEnabled(True)
            self.lE_hash.setText("")
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

    # Функция для чтения хэшей из файла
    def read_hashes_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл '{filename}' не найден.")
        except Exception as e:
            raise Exception(f"Ошибка при чтении файла: {str(e)}")

    # Функция для вычисления SHA-256 хэша строки
    def compute_hash(self, password):
        try:
            return sha256(password.encode()).hexdigest()
        except Exception as e:
            raise Exception(f"Ошибка при вычислении хэша: {str(e)}")

       # Функция для генерации всех комбинаций символов без использования itertools
    def generate_combinations(self, charset, length):
        if length == 0:  # Если длина равна 0, вернуть пустую строку
            yield ""
        else:  # Иначе добавлять символы по одному
            for char in charset:
                for combination in self.generate_combinations(charset, length - 1):
                    yield char + combination 

    # Функция для перебора пароля в однопоточном режиме
    def brute_force(self, target_hash, charset, length):
        try:
            start_time = time.time()
            for combo in self.generate_combinations(charset, length): # Перебираем комбинации
                if self.compute_hash(combo) == target_hash: # Если хэш совпал, возвращаем пароль
                    return combo, time.time() - start_time
            return None, time.time() - start_time
        except Exception as e:
            raise Exception(f"Ошибка при однопоточном переборе: {str(e)}")
           
    # Функция для перебора пароля в многопоточном режиме
    def brute_force_multithread(self, target_hash, charset, length, thread_count):
        try:
            def worker(start, step, result):  # Рабочая функция для потоков
                charset_size = len(charset)  # Количество символов в наборе
                total_combinations = charset_size ** length  # Общее количество комбинаций

                for idx in range(start, total_combinations, step):  # Перебираем комбинации с шагом
                    password = ""  # Текущий пароль
                    temp_idx = idx
                    for _ in range(length):  # Построение пароля из индекса
                        password = charset[temp_idx % charset_size] + password
                        temp_idx //= charset_size

                    if self.compute_hash(password) == target_hash:  # Проверяем хэш
                        result[0] = password  # Сохраняем результат
                        return

            threads = []  # Список потоков
            result = [None]  # Общий результат
            start_time = time.time()

            for t in range(thread_count):  # Создаем и запускаем потоки
                thread = threading.Thread(target=worker, args=(t, thread_count, result))
                threads.append(thread)
                thread.start()

            for thread in threads:  # Ждем завершения всех потоков
                thread.join()
            
            return result[0], time.time() - start_time
        
        except Exception as e:
            raise Exception(f"Ошибка при многопоточном переборе: {str(e)}")

    #Запуск фун-ии
    def run(self):
        charset = ascii_lowercase  # Набор символов (a-z)
        try:
            if self.lE_hash.text() != "" : # Из строки
                hash = self.lE_hash.text()
                if self.cB_1.isChecked(): # Однопоточный режим
                    password, duration = self.brute_force(hash, charset, self.length)
                    self.log_action(f"Пароль: {password if password else 'Не найдено'}, Время: {duration:.2f}с")
                elif self.cB_many.isChecked(): # Многопоточный режим
                    thread_count = self.sB_streams.value()
                    password, duration = self.brute_force_multithread(hash, charset, self.length, thread_count)
                    self.log_action(f"Пароль: {password if password else 'Не найдено'}, Время: {duration:.2f}с")
                else:
                    self.show_error(f"Не выбран режим.") 
            
            elif self.lE_hash2.text() != "": # Из файла
                hash_file = self.lE_hash2.text()
                try:
                    hashes = self.read_hashes_from_file(hash_file)  # Читаем хэши из файла
                except FileNotFoundError:
                    self.show_error(f"Файл {hash_file} не найден. Проверьте путь и имя файла.")
                    return
        
                for target_hash in hashes:  # Обрабатываем каждый хэш
                    if self.cB_1.isChecked(): # Однопоточный режим
                        password, duration = self.brute_force(target_hash, charset, self.length)
                        self.log_action(f"Пароль: {password if password else 'Не найдено'}, Время: {duration:.2f}с")
                    elif self.cB_many.isChecked(): # Многопоточный режим
                        thread_count = self.sB_streams.value()
                        password, duration = self.brute_force_multithread(target_hash, charset, self.length, thread_count)
                        self.log_action(f"Пароль: {password if password else 'Не найдено'}, Время: {duration:.2f}с")
                    else:
                        self.show_error(f"Не выбран режим.")      
            else:
                self.show_error(f"Не введен хэш.")

        except Exception as e:
            self.show_error(f"Ошибка выполнения: {str(e)}") 

    def log_action(self, message):
        self.create_info += "\n ----------------------- -----------------------"
        self.create_info +="\n" + message + "\n"
        self.tE_result.setPlainText(self.create_info)      
            
    def show_error(self, message):
        error1 = QMessageBox()
        error1.setWindowTitle("Ошибка")
        error1.setText(message)
        error1.setIcon(QMessageBox.Icon.Warning)
        error1.setStandardButtons(QMessageBox.StandardButton.Ok)
        error1.exec_() 
        
if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        Login = Window1()
        Login.show()
        sys.exit(app.exec_())
