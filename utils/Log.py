import os
import time

class LogClass:
    logs_folder = 'logs/'
    file_path = ""

    def __init__(self, file_path, file_name):
        self.file_name = file_name
        if not os.path.exists(self.logs_folder):
            os.makedirs(self.logs_folder)
            
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        self.file_path = file_path

    def log(self, message):
        with open(self.file_path+ "/" + self.file_name + '.txt', 'a+') as f:
            f.write(time.strftime("%H:%M:%S") + ': ' + message + '\n')