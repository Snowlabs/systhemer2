import logging
import shlex
import Progs

logger = logging.getLogger('Systhemer.interactive')


class commands(object):
    @staticmethod
    def _quit(S):
        print('exiting interactive mode...')
        exit(0)

    @staticmethod
    def _exec(S, s):
        print(s)
        exec(s)

    @staticmethod
    def reload_progdefs(S):
        Progs.setup(S)


def run(Settings):
    def run_cmd(cmd, args=[]):
        if args:
            cmd(Settings, *args)
        else:
            cmd(Settings)
    try:
        while True:
            # get input
            command = input('> ')

            # skip empty line
            if not command:
                continue

            # parse input
            command = shlex.split(command)
            command, *args = command
            logger.log(Settings.VDEBUG,
                       'cmd: \'%s\', args: %s' % (command, args))

            # replace '-' chars with '_' in command
            command = ''.join([c if c != '-' else '_' for c in command])

            # run command with args
            # it tries to find the command in commands and then
            # _command and if nothing is found then cmd=None
            cmd = getattr(commands, command,
                          getattr(commands, '_'+command,
                                  None))
            if cmd:
                run_cmd(cmd, args)
            else:
                print('Error: command not found!')

    # handle KeyboardInterrupt
    except KeyboardInterrupt:
        print()
        run_cmd(commands.quit)
