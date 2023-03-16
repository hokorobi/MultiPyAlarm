# -*- coding: utf-8 -*-
from logging import getLogger, Formatter, FileHandler, INFO
from pathlib import Path
import sys


class Logger(object):
    def __init__(self):
        self.logger = getLogger(__name__)
        self.handler = FileHandler(
            Path(sys.argv[0]).resolve().parent / "MultiPyAlarm.log"
        )
        self.handler.setLevel(INFO)
        formatter = Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
        self.handler.setFormatter(formatter)
        self.logger.setLevel(INFO)
        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def timer(self, action, timer):
        self.logger.info(
            f"[{action}] message: {timer['message']}, starttime: {timer['starttime']}, endtime: {timer['endtime']}"
        )
