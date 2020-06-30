from utils.argument import get_main_argument
from utils.log import get_logger
from os.path import join, exists
from os import makedirs
import torch
import random
import numpy as np
import warnings
import os

def init_rng(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    torch.random.manual_seed(seed)


def create_dir(dir_path):
    if not exists(dir_path):
        makedirs(dir_path)


class Context:
    def __init__(self, desc="Transformer", config=None, logger=None):
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

        # self.logger.debug("The Input Parameters:")
        # for key, val in self.config.items():
        #     self.logger.debug(f"{key} => {val}")


        # Trainning Device Set up
        self.device = torch.device(self.config["device"])
        self.device_id = list(self.config["device_id"])
        self.is_cuda = self.config["device"] == 'cuda'
        self.is_cpu = self.config["device"] == 'cpu'
        self.is_gpu_parallel = self.is_cuda and (len(self.device_id) > 1)

        init_rng(seed=0)
        # os.environ['CUDA_VISIBLE_DEVICES'] = str(self.device_id[0])
        warnings.filterwarnings('ignore')

    def mapping_to_cuda(self, tensor):
        return tensor.to(self.device) if tensor is not None and self.is_cuda else tensor
