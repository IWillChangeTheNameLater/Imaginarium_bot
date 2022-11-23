def discord_import():
    from bots.discord_bot.main import main
    main()


bots_run_scripts = {'Discord': discord_import}

while True:
    try:
        bots_run_scripts[input('Specify the bot you want to run: ')]()
    except KeyError:
        print('There are no bots with that name here. \n' +
              'Type one of the following: \n' +
              ' — ' + '\n — '.join(bots_run_scripts.keys()) + '\n')
