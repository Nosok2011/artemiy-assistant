# ассистент создан с помощью урока от хауди хо: https://www.youtube.com/watch?v=YeS755SPSI8
from random import choice
from jsonc import loads, dumps
from fuzzywuzzy import fuzz
from datetime import datetime
from geopy.geocoders import Nominatim
from requests import get
from sys import exit
from currencyapicom import Client
from math import floor
settings = loads(open("settings.jsonc", encoding="UTF-8").read())
def round_1(num):
    num_ = (num * 10) % 10
    num = floor(num)
    num += 1 if num_ >= 5 else 0
    return num
def get_api_key(for_, setting_name):
    api = input(f"Введите ключ API для {for_}: ")
    settings["settings"][setting_name] = api
    edit_settings(settings)
    print("Ключ сохранён.")
    return api
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
    print(cmd) if settings["settings"]["debug_mode"] else 0
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
                print(choice(settings["answers"]["disable_welcome_message"]))
            case "enable_welcome_message":
                print(exec_msg)
                settings["settings"]["welcome_message_enabled"] = True
                edit_settings(settings)
                print(done_msg)
                print(choice(settings["answers"]["enable_welcome_message"]))
            case "exit":
                print(choice(settings["answers"]["exit"]))
                exit()
            case "help":
                print(f"{choice(settings["answers"]["help"])} (полный список см. по ссылке https://clck.ru/38Xg5s в разделе \"Возможности\"):")
                help_ = [
                    "1. Узнавать время",
                    "2. Узнавать дату",
                    "3. Узнавать погоду",
                    "4. Узнавать курс рубля",
                    "5. Подбрасывать монетку"
                ]
                help_ = "\n".join(help_)
                print(help_)
            case "weather":
                addr = input("Введите адрес, где хотите узнать погоду: ")
                locator = Nominatim(user_agent="Yandex")
                location = locator.geocode(addr)
                addr_ = location.address
                lat, lon = location.latitude, location.longitude
                w_api = settings["settings"]["weather_api_key"]
                w_api = get_api_key("weatherapi.com", "weather_api_key") if w_api == 0 else w_api
                req = get(f"http://api.weatherapi.com/v1/current.json?key={w_api}&q={lat},{lon}&lang=ru").json()
                if "error" in req.keys():
                    err = req["error"]
                    print("Ошибка выполнения запроса.")
                    print(f"Код ошибки: {err["code"]}")
                    print(f"Описание ошибки: {err["message"]}")
                else:
                    cur = req["current"]
                    print(choice(settings["answers"]["weather"]) % addr_ + ":")
                    print(f"Температура: {int(cur["temp_c"])}°C")
                    print(f"Ощущается как: {int(cur["feelslike_c"])}°C")
                    print(f"Описание: {cur["condition"]["text"]}")
                    print(f"Скорость ветра: {int(cur["wind_kph"] * 1000 / 3600)} м/с")
                    print(f"Давление: {int(cur["pressure_mb"] * 0.750063755419211)} мм рт. ст.")
                    print(f"Влажность: {cur["humidity"]}%")
                    print(f"Облачность: {cur["cloud"]}%")
            case "currency":
                c_api = settings["settings"]["currency_api_key"]
                c_api = get_api_key("currencyapi.com", "currency_api_key") if c_api == 0 else c_api
                client = Client(c_api)
                usd = client.latest("USD", ["RUB"])["data"]["RUB"]["value"]
                eur = client.latest("EUR", ["RUB"])["data"]["RUB"]["value"]
                print(f"1$ = {round_1(usd)}₽")
                print(f"1€ = {round_1(eur)}₽")
            case "flip_coin":
                coin = ["орёл", "решка"]
                rnd = choice(coin)
                print(f"{rnd.capitalize()}.")
            case _:
                print(choice(settings["answers"]["not_implemented"]))
    else:
        match cmd["cmd"]:
            case "debug_mode":
                print(exec_msg)
                settings["settings"]["debug_mode"] = not settings["settings"]["debug_mode"]
                edit_settings(settings)
                print(done_msg)
                print(
                    "Активирован режим отладки. В этом режиме перед выполнением каждой команды будут выводиться её данные в виде словаря python."
                    if settings["settings"]["debug_mode"]
                    else "Режим отладки деактивирован."
                )
            case _:
                print(choice(settings["answers"]["unknown"]))
print(choice(settings["answers"]["welcome"])) if settings["settings"]["welcome_message_enabled"] else 0
while True:
    query = input(">>> ")
    cmd = recog_cmd(query)
    exec_cmd(cmd)