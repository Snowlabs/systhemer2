import Progs


def tree(args):
    args = args.split()
    if len(args) < 1:
        print('Not enough arguments! '
              'Please provide target for tree command')
        return

    target = args.pop(0)
    for pd in Progs.prog_defs:
        if target == pd.get_name():
            print(target)
            print('├')
