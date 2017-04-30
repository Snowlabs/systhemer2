import Progs.value as _value


def value(self, args):
    """Usage: value [val_type] [val]"""
    args = args.split()

    if len(args) < 2:
        print('Not enough arguments!')
        return
    print(eval('repr(_value.{}.Formatter.auto_parse(\'{}\'))'.format(*args)))
