from argparse import ArgumentParser


def config_opts(parser):
    parser.add_argument('-config', '--config', required=True, help='Config file path')
    parser.add_argument('-project_dir', '--project_dir', type=str, default='')
    parser.add_argument('-project_log', '--project_log', type=str, default='')
    parser.add_argument('-debug', '--debug', type=str, default="False")


def party_opts(parser):
    parser.add_argument('-host', '--host', type=str)
    parser.add_argument('-port', '--port', type=int)
    parser.add_argument('-party_id', '--party_id', type=int, default=0)


def client_opts(parser):
    parser.add_argument('-nums_party', '--nums_party', type=int, default=5)
    parser.add_argument('-operation', '--operation', type=str, default='=', choices=['+', '-', '=', '*'])
    parser.add_argument('-op1', '--op1', type=str, default="")
    parser.add_argument('-op2', '--op2', type=str, default="")


def get_default_argument(desc='default'):
    parser = ArgumentParser(description=desc)
    config_opts(parser)
    if desc == 'party':
        party_opts(parser)
    elif desc == 'client':
        client_opts(parser)
    else:
        party_opts(parser)
        client_opts(parser)
    args = parser.parse_args()
    config = vars(args)
    return config
