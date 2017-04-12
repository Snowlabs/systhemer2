import Progs


def tree(self, args):
    """usage: tree TARGET

    Illustrate the hierarchy tree of TARGET
    Inspired by common `tree` command in most unix-based systems
    """
    args = args.split()
    if len(args) < 1:
        print('Not enough arguments! '
              'Please provide target for tree command')
        return

    target = args.pop(0)
    for pd in Progs.prog_defs:
        if target == pd.get_name():
            print(pd.get_config())
            for i, b in enumerate(pd.get_config()):
                if i == len(pd.get_config())-1:
                    elbow = True
                else:
                    elbow = False
                recur(b, [], [], elbow)


def recur(branch, sep_array, seps, elbow):
    print('%s%s─%s' % (''.join(sep_array), '└' if elbow else '├', branch))
    if isinstance(branch, Progs.common.Section):
        sep_array.append('  ' if elbow else '│ ')
        for i, b in enumerate(branch):
            if i == len(branch)-1:
                elbow = True
            else:
                elbow = False
            recur(b, sep_array, seps, elbow)
