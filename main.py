def discord_import():
    import bots.discord_bot.main
    bots.discord_bot.main.main()


bots_run_scripts = {'Discord': discord_import}


def main():
    while True:
        try:
            bots_run_scripts[input('Specify the bot you want to run: ')]()
        except KeyError:
            print('There are no bots with that name here. \n' +
                  'Type one of the following: \n' +
                  ' — ' + '\n — '.join(bots_run_scripts.keys()) + '\n')


if __name__ == '__main__':
    main()
