
class File:
    def __init__(self, file_name):
        self.file_name = file_name
        self.file_pointer = open_file(file_name)

    def read(self):
        return read_data(self.file_pointer)

    def write(self, data):
        write_data(self.file_pointer, data)

    def close(self):
        close_file(self.file_pointer)
