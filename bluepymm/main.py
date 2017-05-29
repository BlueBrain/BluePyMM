import argparse

from bluepymm import prepare_combos, run_combos, select_combos


def get_parser():
    '''return the argument parser'''
    parser = argparse.ArgumentParser()
    actions = parser.add_subparsers(help='actions', dest='action')

    prepare_combos.add_parser(actions)
    run_combos.add_parser(actions)
    select_combos.add_parser(actions)

    return parser


def main(arg_list):
    """Main"""

    print('\n######################################')
    print('# Blue Brain Python Model Management #')
    print('######################################\n')

    args = get_parser().parse_args(arg_list)

    if args.action == "prepare":
        prepare_combos.prepare_combos(conf_filename=args.conf_filename,
                                      continu=args.continu)
    elif args.action == "run":
        run_combos.run_combos(conf_filename=args.conf_filename,
                              ipyp=args.ipyp,
                              ipyp_profile=args.ipyp_profile)
    elif args.action == "select":
        select_combos.select_combos(conf_filename=args.conf_filename)
