import logging
import cmd
import Progs


class iconsole(cmd.Cmd):
    def __init__(self, Settings, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.Settings = Settings
        self.logger = logging.getLogger('Systhemer.interactive')

    intro = 'Welcome to the Systhemer console!'
    prompt = '> '
    file = None

    def do_quit(self, args):
        print('exiting interactive mode...')
        exit(0)

    def do_exec(self, args):
        print(args)
        exec(args[0])

    def do_reload_progdefs(self, args):
        Progs.setup(self.Settings)
