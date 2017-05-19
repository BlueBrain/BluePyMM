import sys

from bluepymm import prepare_and_run_combos as mm
from bluepymm import select_combos as megate


def main(arg_list=None):
    if arg_list is None:
        arg_list = sys.argv[1:]
    mode = arg_list[0]

    if mode == "mm":
        mm.main(arg_list[1:])
    elif mode == "megate":
        megate.main(arg_list[1:])
    else:
        print('Unknown command {}'.format(mode))
        print('Known commands are: mm, megate')


if __name__ == "__main__":
    main()
