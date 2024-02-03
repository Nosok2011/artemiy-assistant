# ассистент создан с помощью урока от хауди хо: https://www.youtube.com/watch?v=YeS755SPSI8
from random import choice
from jsonc import loads, dumps
from fuzzywuzzy import fuzz
from datetime import datetime
from geopy.geocoders import Nominatim
from requests import get
settings = loads(open("settings.jsonc", encoding="UTF-8").read())
locator = Nominatim(user_agent="Yandex")
def edit_settings(new):
    settings_ = open("settings.jsonc", "w", encoding="UTF-8")
    comment = [
        "// в этой директории существует файл \"settings_orig.jsonc\".",
        "// он нужен для того, чтобы возвращаться к заводским настройкам.",
        "// нужно просто скопировать содержимое оригинального файла в этот.\n"
    ]
    comment = "\n".join(comment)
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
    exec_msg = choice(settings["answers"]["executing"])
    done_msg = choice(settings["answers"]["done"])
    if cmd["ratio"] >= 50:
        match cmd["cmd_name"]:
            case "time":
                now = datetime.now()
                print(choice(settings["answers"]["time"]) % (now.hour, now.minute, now.second))
            case "date":
                today = datetime.today()
                print(choice(settings["answers"]["date"]) % (today.day, today.month, today.year))
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
                print(f"{choice(settings["answers"]["help"])} (полный список см. по ссылке https://clck.ru/38Xg5s в разделе \"Возможности\"):")
                help_ = [
                    "1. Узнавать время",
                    "2. Узнавать дату",
                    "3. Узнавать погоду"
                ]
                help_ = "\n".join(help_)
                print(help_)
            case "weather":
                addr = input("Введите адрес, где хотите узнать погоду: ")
                location = locator.geocode(addr)
                addr_ = location.address
                lat, lon = location.latitude, location.longitude
                api = settings["settings"]["weather_api_key"]
                if api == 0:
                    api = input("Введите ключ API для api.weatherapi.com: ")
                    settings["settings"]["weather_api_key"] = api
                    edit_settings(settings)
                    print("Ключ сохранён.")
                req = get(f"http://api.weatherapi.com/v1/current.json?key={api}&q={lat},{lon}&lang=ru").json()
                cur = req["current"]
                print(choice(settings["answers"]["weather"]) % addr_ + ":")
                print(f"Температура: {int(cur["temp_c"])}°C")
                print(f"Ощущается как: {int(cur["feelslike_c"])}°C")
                print(f"Описание: {cur["condition"]["text"]}")
                print(f"Скорость ветра: {int(cur["wind_kph"] * 1000 / 3600)} м/с")
                print(f"Давление: {int(cur["pressure_mb"] * 0.750063755419211)} мм рт. ст.")
                print(f"Влажность: {cur["humidity"]}%")
                print(f"Облачность: {cur["cloud"]}%")
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