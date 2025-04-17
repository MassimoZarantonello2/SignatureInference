import os
import time

class LogClass:
    file_path = 'logs/'
    file_name = 'log.txt'

    def __init__(self, file_path, file_name):
        self.file_name = file_name
        if not os.path.exists('logs/'):
            os.makedirs('logs/')
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        self.file_path = file_path

    def log(self, message):
        with open("logs/" + self.file_path + self.file_name + 'txt', 'a+') as f:
            f.write(time.strftime("%H:%M:%S") + ': ' + message + '\n')