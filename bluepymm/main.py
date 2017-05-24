from bluepymm import prepare_combos, run_combos, select_combos


def _print_help():
    prepare_combos.print_help()
    print('')
    run_combos.print_help()
    print('')
    select_combos.print_help()


def main(arg_list):
    """Main"""

    print('\n##########################################################')
    print('# Starting BluePyMM: Blue Brain Project Model Management #')
    print('##########################################################\n')

    if arg_list:
        mode = arg_list[0]

        if mode == "prepare":
            prepare_combos.main(arg_list[1:])
        elif mode == "run":
            run_combos.main(arg_list[1:])
        elif mode == "select":
            select_combos.main(arg_list[1:])
        elif "help" in mode:
            _print_help()
        else:
            print('Unknown command {}'.format(mode))
            print('Known commands are: help, prepare, run, select')
    else:
        _print_help()
