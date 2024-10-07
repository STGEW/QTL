RC_FILE_PATH = '../data/rc.txt'


class RC:

    def __init__(self):
        self.raw_data = []
        with open(RC_FILE_PATH, 'r') as f:
            for l in f.read():
                self.raw_data.append(l)

    def read(self):
        if self.raw_data:
            values = self.raw_data.pop(0).split(' ')
            data = {}
            for i in range(len(values)):
                data[str(i + 1)] = values[i]
            return data
        else:
            raise ValueError("No more data from RC available")
