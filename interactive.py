import shlex
import Progs

class commands(object):
    @staticmethod
    def quit():
        print('\nexiting interactive mode...')
        exit(0)

def run(Settings):
    try:
        while True:
            command = input('> ')
            if not command:
                continue
            command = shlex.split(command)
            print(command)
            if command[0] in dir(commands):
                if command[0] != 'run':
                    exec('commands.' + command[0]
                         + '(' + ', '.join(command[1:]) + ')')
            else:
                print('Error: command not found!')
    except KeyboardInterrupt:
        commands.quit()
