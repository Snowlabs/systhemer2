import shlex
import Progs


class commands(object):
    @staticmethod
    def quit(S):
        print('exiting interactive mode...')
        exit(0)

    @staticmethod
    def reload_progdefs(S):
        Progs.setup(S)

    @staticmethod
    def exec(S, s):
        exec(s)


def run(Settings):
    def run_cmd(cmd, args=[]):
        if args:
            cmd(Settings, eval(', '.join(args)))
        else:
            cmd(Settings)
    try:
        while True:
            command = input('> ')
            if not command:
                continue
            command = shlex.split(command)
            print(command)
            if command[0] in dir(commands):
                run_cmd(eval('commands.' + command[0]), command[1:])
            else:
                print('Error: command not found!')
    except KeyboardInterrupt:
        print()
        run_cmd(commands.quit)
