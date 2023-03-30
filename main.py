from sys import executable
from subprocess import Popen
from pathlib import Path
from typing import Callable, Mapping, MutableMapping
from time import sleep

bots_init_files: Mapping[str, Path | str] = {
    'Discord': Path(__file__).parent / 'bots' / 'discord_bot' / 'main.py',
}
bots_processes: MutableMapping[str, Popen] = {}


def require_bot_name() -> str:
    bot = None
    while True:
        bot = input("Input the bot's name: ")

        if bots_init_files.get(bot):
            break
        else:
            print('This bot does not exist. Try one of the following: \n' +
                  ', '.join([b for b in bots_init_files.keys()]))

    return bot


def run_bot(bot: str) -> bool:
    if bot in bots_processes:
        return False
    else:
        bots_processes[bot] = Popen([executable, bots_init_files[bot]])
        # Wait for the process to start,
        # otherwise the input will block it.
        sleep(1)

        return True


def stop_bot(bot: str) -> bool:
    if bot in bots_processes:
        bots_processes[bot].terminate()
        del bots_processes[bot]

        return True
    else:
        return False


def rerun_bot(bot) -> bool:
    return stop_bot(bot) and run_bot(bot)


class Commands:
    @staticmethod
    def help():
        msg = ('Try to run one of the following functions to perform an action: \n' +
               ', '.join([c for c in dir(Commands)
                          if not any((c.startswith('__'), c.endswith('__')))]))

        print(msg)

    @staticmethod
    def run_bot() -> None:
        bot = require_bot_name()

        if run_bot(bot):
            print(f'The "{bot}" bot is run.')
        else:
            print(f'The "{bot}" bot cannot be run.')

    @staticmethod
    def stop_bot() -> None:
        bot = require_bot_name()

        if stop_bot(bot):
            print(f'The "{bot}" bot is stopped.')
        else:
            print(f'The "{bot}" bot cannot be stopped.')

    @staticmethod
    def rerun_bot() -> None:
        bot = require_bot_name()

        if rerun_bot(bot):
            print(f'The "{bot}" bot is rerun.')
        else:
            print(f'The "{bot}" bot cannot be rerun.')


def require_command() -> Callable[[], None]:
    while True:
        command = input('Input the command: ')

        if not hasattr(Commands, command):
            print('This command does not exist. Try one of the following: \n' +
                  ', '.join([c for c in dir(Commands)
                             if not any((c.startswith('__'), c.endswith('__')))]))
        else:
            break

    return getattr(Commands, command)


def main():
    while True:
        command = require_command()
        command()


if __name__ == '__main__':
    main()
