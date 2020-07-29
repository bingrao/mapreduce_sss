from argparse import ArgumentParser


def config_opts(parser):
    parser.add_argument('-config', '--config', required=True, help='Config file path')
    parser.add_argument('-project_dir', '--project_dir', type=str, default='')
    parser.add_argument('-project_log', '--project_log', type=str, default='')
    parser.add_argument('-debug', '--debug', type=bool, default=False)
    parser.add_argument('-vss', '--vss', type=str, default="Feldman",
                        choices=['None', 'Feldman', 'Pedersen'])


def party_opts(parser):
    parser.add_argument('-nums_server', '--nums_server', type=int, default=5)


def client_opts(parser):
    parser.add_argument('-nums_party', '--nums_party', type=int, default=5)

    # Mathematical Computation
    group = parser.add_argument_group('Mathematical Computation')
    group.add_argument('-math_op', '--math_op', type=str, default='=', choices=['+', '-', '=', '*'])
    group.add_argument('-op1', '--op1', type=int, default=1)
    group.add_argument('-op2', '--op2', type=int, default=1)

    group = parser.add_argument_group('String Operation')
    group.add_argument('-str_op', '--str_op', type=str, default='match', choices=['match', 'count'])
    group.add_argument('-str1', '--str1', type=str, default=1)
    group.add_argument('-str2', '--str2', type=str, default=1)

    group = parser.add_argument_group('Dataframe (Table/Database) Operation')
    group.add_argument('-data', '--data', type=str, default="data/employee-attrition.csv")
    group.add_argument('-df_op', '--df_op', type=str, default='match',
                       choices=['match', 'join', 'selection', 'range_search'])


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
