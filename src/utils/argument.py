from argparse import ArgumentParser
# import torch


def get_main_argument(desc='Train Transformer'):
    parser = ArgumentParser(description=desc)
    # Command Project Related Parameters
    parser.add_argument('--project_log', type=str, default="")
    # parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--device_id', type=list, default=[0])
    parser.add_argument('--debug', type=str, default="False")
    parser.add_argument('--party_id', type=int, default=0)
    parser.add_argument('--party_size', type=int, default=5)
    args = parser.parse_args()
    config = vars(args)
    return config
