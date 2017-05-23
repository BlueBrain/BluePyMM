import sys

from bluepymm import prepare_combos, run_combos, select_combos


def main(arg_list):
    """Main"""

    print('\n#####################')
    print('# Starting BluePyMM #')
    print('#####################\n')

    mode = arg_list[0]

    if mode == "prepare":
        prepare_combos.main(arg_list[1:])
    elif mode == "run":
        run_combos.main(arg_list[1:])
    elif mode == "select":
        select_combos.main(arg_list[1:])
    else:
        print('Unknown command {}'.format(mode))
        print('Known commands are: prepare, run, select')


if __name__ == "__main__":
    main(sys.argv[1:])
