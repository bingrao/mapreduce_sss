from utils.argument import get_main_argument
from utils.log import get_logger
from os.path import join, exists
from os import makedirs
# import torch
import random
import numpy as np
import warnings
import os


def init_rng(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    # torch.random.manual_seed(seed)


def create_dir(dir_path):
    if not exists(dir_path):
        makedirs(dir_path)


class Context:
    def __init__(self, desc="MapReduce_Secret_Share", config=None, logger=None):
        self.description = desc
        self.project_raw_dir = "../src"
        # A dictionary of Config Parameters
        self.config = get_main_argument(desc=self.description)
        if config is not None:
            self.config.update(config)

        self.project_log = self.config["project_log"]
        if not exists(self.project_log):
            self.project_log = join(os.path.dirname(self.project_raw_dir), 'logs', 'log.txt')
            create_dir(os.path.dirname(self.project_log))

        # logger interface
        self.isDebug = True
        self.logger = get_logger(self.description, self.project_log, self.isDebug) if logger is None else logger
        self.logger.debug("The logger interface is initited ...")

        self.userClient = "localhost", 9001
        self.dbServer = "localhost", 9002

        self.partyServers = [("localhost", 8000),
                             ("localhost", 8001),
                             ("localhost", 8002),
                             ("localhost", 8003),
                             ("localhost", 8004),
                             ("localhost", 8005),
                             ("localhost", 8006),
                             ("localhost", 8007),
                             ("localhost", 8008),
                             ("localhost", 8009)]

        self.party_id = self.config["party_id"]
        self.party_size = self.config["party_size"]

        init_rng(seed=0)
        warnings.filterwarnings('ignore')

    def mapping_to_cuda(self, tensor):
        return tensor.to(self.device) if tensor is not None and self.is_cuda else tensor
