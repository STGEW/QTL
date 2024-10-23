import logging
from consts import DATA_DIR


RC_FILE_PATH = f'../{DATA_DIR}/rc.txt'


logger = logging.getLogger(__name__)


class RC:

    def __init__(self):
        self.raw_data = []
        logger.info(f"RC file name: '{RC_FILE_PATH}'")
        with open(RC_FILE_PATH, 'r') as f:
            self.raw_data = [line.strip() for line in f]
            logger.info(f"Read rc file lines: '{self.raw_data}'")

    def read(self):
        if self.raw_data:
            l = self.raw_data.pop(0)
            logger.info(f"Line: '{l}'")
            values = l.split(' ')
            logger.info(f"Values: '{values}'")
            data = {}
            for i in range(0, len(values)):
                data[str(i + 1)] = float(values[i])
            logger.info(f"RC data: '{data}'")
            return data
        else:
            raise ValueError("No more data from RC available")
