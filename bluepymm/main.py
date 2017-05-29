from bluepymm import prepare_combos, run_combos, select_combos


def print_help(help_mode=None):
    """Print help"""

    if help_mode == "prepare":
        prepare_combos.print_help()
    elif help_mode == "run":
        run_combos.print_help()
    elif help_mode == "select":
        select_combos.print_help()
    else:
        print("""Usage:

  bluepymm <command>

Commands:
  prepare   Prepare combos
  run       Run combos
  select    Select combos
  help      Show help for commands
""")
        if help_mode is not None:
            print("ERROR: Unknown command: %s" % help_mode)


def main(arg_list):
    """Main"""

    print('\n######################################')
    print('# Blue Brain Python Model Management #')
    print('######################################\n')

    if arg_list:
        mode = arg_list[0]

        if mode == "prepare":
            prepare_combos.main(arg_list[1:])
        elif mode == "run":
            run_combos.main(arg_list[1:])
        elif mode == "select":
            select_combos.main(arg_list[1:])
        elif mode == "help":
            try:
                help_mode = arg_list[1]
            except IndexError:
                help_mode = None
            print_help(help_mode=help_mode)
        else:
            print_help()
            print("ERROR: Unknown command: %s" % mode)
    else:
        print_help()
