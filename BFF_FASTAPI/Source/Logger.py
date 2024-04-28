"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [23.04.24]
Purpose: [Logging system.]
"""

import logging
import os
import sys


class Logger:
    def __init__(self, directory='Log', file_name='Server.log',
                 console_log=True, data_format='%(asctime)s [%(levelname)s]: %(message)s',
                 date_format='%Y-%m-%d %H:%M:%S'):
        """
        Initialize Logger class.

        :param directory: Directory to store log files.
        :param file_name: Name of the log file.
        :param console_log: Flag indicating whether to log messages to the console.
        :param data_format: Format of the log messages.
        :param date_format: Format of the date in log messages.
        """
        self.directory = directory
        self.file_name = file_name
        self.console_log = console_log
        self.full_path = os.path.join(self.directory, self.file_name)
        self.data_format = data_format
        self.date_format = date_format

        os.makedirs(self.directory, exist_ok=True)

        self.setup_logger()

        if self.console_log:
            self.access_console_log()

    def setup_logger(self):
        """
        Setup logger configuration.
        Configures the logger with specified settings.
        """
        logging.basicConfig(
            filename=self.full_path,
            level=logging.INFO,
            format=self.data_format,
            datefmt=self.date_format
        )

    def access_console_log(self):
        """
        Access console log.
        Adds a console handler to the logger to enable logging to the console.
        """
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(self.data_format, self.date_format))
        logging.getLogger().addHandler(console_handler)
