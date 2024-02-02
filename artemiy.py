# ассистент создан с помощью урока от хауди хо: https://www.youtube.com/watch?v=YeS755SPSI8
from random import choice
from jsonc import loads, dumps
from fuzzywuzzy import fuzz
settings = loads(open("settings.json", encoding="UTF-8").read())
def edit_settings(new):
    settings_ = open("settings.json", "w", encoding="UTF-8")
    comment = """// в этой директории существует файл \"settings_orig.json\".
                 // он нужен для того, чтобы возвращаться к заводским настройкам.
                 // нужно просто скопировать содержимое оригинального файла в этот.\n"""
    comment = "\n".join(comment.split("\n"))
    comment = comment.replace(" " * 17, "")
    settings_.write(comment + dumps(new, indent=4, ensure_ascii=False))
    settings_.close()
    print("Внимание!! Были изменены настройки. Перезапустите ассистента для полного принятия изменений.")
def recog_cmd(cmd):
    pars = {"cmd": cmd, "cmd_name": "", "ratio": 0} # pars типо parameters
    for name, opts in settings["cmds"].items():
        for opt in opts:
            ratio = fuzz.ratio(cmd, opt)
            if ratio > pars["ratio"]:
                pars["cmd_name"] = name
                pars["ratio"] = ratio
    return pars
def exec_cmd(cmd):
    if settings["settings"]["debug_mode"]:
        print(cmd)
    from datetime import datetime # импортируем здесь, а не в начале, чтобы показывало текущее время и дату, а не на момент запуска
    now = datetime.now()
    exec_msg = choice(settings["answers"]["executing"])
    done_msg = choice(settings["answers"]["done"])
    if cmd["ratio"] >= 50:
        match cmd["cmd_name"]:
            case "time":
                print(choice(settings["answers"]["time"]) % (now.hour, now.minute, now.second))
            case "date":
                print(choice(settings["answers"]["date"]) % (now.day, now.month, now.year))
            case "disable_welcome_message":
                print(exec_msg)
                settings["settings"]["welcome_message_enabled"] = False
                edit_settings(settings)
                print(done_msg)
            case "enable_welcome_message":
                print(exec_msg)
                settings["settings"]["welcome_message_enabled"] = True
                edit_settings(settings)
                print(done_msg)
            case "exit":
                print(choice(settings["answers"]["exit"]))
                exit()
            case "help":
                print(choice(settings["answers"]["help"]))
            case _:
                print(choice(settings["answers"]["unknown"]))
    else:
        match cmd["cmd"]:
            case "debug_mode_on":
                print(exec_msg)
                settings["settings"]["debug_mode"] = True
                edit_settings(settings)
                print(done_msg)
                print("Активирован режим отладки. В этом режиме перед выполнением каждой команды будут выводиться её данные в виде словаря python.")
            case "debug_mode_off":
                print(exec_msg)
                settings["settings"]["debug_mode"] = False
                edit_settings(settings)
                print(done_msg)
                print("Режим отладки деактивирован.")
            case _:
                print(choice(settings["answers"]["unknown"]))
if settings["settings"]["welcome_message_enabled"]:
    print(choice(settings["answers"]["welcome"]))
while True:
    query = input(">>> ")
    cmd = recog_cmd(query)
    exec_cmd(cmd)