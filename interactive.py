""" Interactive mode for Systhemer """

import logging
import cmd
import Progs


class Iconsole(cmd.Cmd):
    """ Interactive console cmd.Cmd subclass """
    def __init__(self, Settings, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.settings = Settings
        self.logger = logging.getLogger('Systhemer.interactive')

    intro = 'Welcome to the Systhemer console!'
    prompt = '> '
    file = None

    def do_quit(self, args):
        """ quit from console """
        print('exiting interactive mode...')
        exit(0)

    def do_exec(self, args):
        """ execute python code """
        print(args)
        exec(args[0])

    def do_reload(self, args):
        """ reload `target` """
        args = args.split()
        sub_cmd = args.pop(0)
        if sub_cmd == 'prog-defs':
            Progs.setup(self.settings)
        else:
            print('Error: subcommand not found \'%s\'' % sub_cmd)

    def do_tree(self, args):
        """ generate nice tree representation of target """
        args = args.split()
        target = args.pop(0)
        for pd in Progs.prog_defs:
            if target == pd.get_name():
                print(target)
                print('├')
