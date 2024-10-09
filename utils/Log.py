import os
import time

class LogClass:
    file_path = 'logs/'
    file_name = 'log.txt'

    def __init__(self, file_name):
        self.file_name = file_name

    def log(self, message):
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        with open(self.file_path + self.file_name, 'a+') as f:
            f.write(time.strftime("%H:%M:%S") + ': ' + message + '\n')