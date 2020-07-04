from src.utils.argument import get_default_argument
from src.utils.log import get_logger
from os import makedirs
import random
import numpy as np
import warnings
from os.path import dirname, abspath, join, exists
import os

BASE_DIR = dirname(dirname(abspath(__file__)))


def init_rng(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    # torch.random.manual_seed(seed)


def create_dir(dir_path):
    if not exists(dir_path):
        makedirs(dir_path)


class Context:
    def __init__(self, desc):

        assert desc == 'party' or desc == 'client' or desc == 'default'

        self.desc = desc
        # A dictionary of Config Parameters
        self.config = get_default_argument(desc=self.desc)

        self.project_dir = self.config['project_dir'] if self.config['project_dir'] != "" \
            else str(BASE_DIR)

        self.project_log = self.config["project_log"]
        if not exists(self.project_log):
            self.project_log = join(os.path.dirname(self.project_dir), 'logs', 'log.txt')
            create_dir(os.path.dirname(self.project_log))

        # logger interface
        self.isDebug = self.config['debug']
        self.logger = get_logger(self.desc, self.project_log, self.isDebug)

        if self.config['config'] is not None:
            with open(self.config['config']) as config_file:
                import yaml
                config_content = yaml.safe_load(config_file)
            self.partyServers = [(x['host'], x['port']) for x in config_content['servers']]

        else:
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

        self.max_nums_server = len(self.partyServers)
        if self.desc != 'client':
            self.nums_server = self.config['nums_server']
            assert self.nums_server <= self.max_nums_server

        if self.desc == 'client':
            self.nums_party = self.config['nums_party']
            assert self.nums_party <= self.max_nums_server

        init_rng(seed=0)
        warnings.filterwarnings('ignore')

    def mapping_to_cuda(self, tensor):
        return tensor.to(self.device) if tensor is not None and self.is_cuda else tensor
