import logging
import os
import sys


class Logger:
    def __init__(self, directory='Log', filename='Server.log',
                 console_log=True, data_format='%(asctime)s [%(levelname)s]: %(message)s',
                 date_format='%Y-%m-%d %H:%M:%S'):
        self.directory = directory
        self.filename = filename
        self.console_log = console_log
        self.full_path = os.path.join(self.directory, self.filename)
        self.data_format = data_format
        self.date_format = date_format

        os.makedirs(self.directory, exist_ok=True)  # Создаем директорию, если её нет

        self.setup_logger()

        if self.console_log:
            self.access_console_log()

    def setup_logger(self):
        # Настройка логгера

        logging.basicConfig(
            filename=self.full_path,  # Имя файла для сохранения логов
            level=logging.INFO,  # Уровень логирования
            format=self.data_format,  # Формат сообщений
            datefmt=self.date_format  # Формат времени
        )

    def access_console_log(self):
        # Добавляем обработчик для вывода логов в консоль

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(self.data_format, self.date_format))
        logging.getLogger().addHandler(console_handler)
