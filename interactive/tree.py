class tree(object):
    def __init__(self, S):
        self.Settings = S

    def run(self, args):
        args = args.split()
        target = args.pop(0)
        for pd in Progs.prog_defs:
            if target == pd.get_name():
                print(target)
                print('├')
