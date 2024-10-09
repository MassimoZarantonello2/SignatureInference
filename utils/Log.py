class LogClass:
    file_path = 'logs/'
    file_name = 'log.txt'

    def __init__(self, file_name):
        self.file_name = file_name
        pass

    @staticmethod
    def log(message):
        with open(LogClass.file_path + LogClass.file_name, 'a') as f:
            f.write(message + '\n')