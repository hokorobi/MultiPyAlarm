# -*- coding: utf-8 -*-
from logging import getLogger, Formatter, FileHandler, INFO

class Logger(object):
    def __init__(self):
        self.logger = getLogger(__name__)
        self.handler = FileHandler('MultiPyAlarm.log')
        self.handler.setLevel(INFO)
        formatter = Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
        self.handler.setFormatter(formatter)
        self.logger.setLevel(INFO)
        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def print(self, s):
        self.logger.info(s)

