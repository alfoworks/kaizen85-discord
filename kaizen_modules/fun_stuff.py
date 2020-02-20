import os
import random

import discord
import requests
from bs4 import BeautifulSoup

import kaizen85modules

emojiDict = {"a": "🇦", "b": "🇧", "c": "🇨", "d": "🇩", "e": "🇪", "f": "🇫", "g": "🇬", "h": "🇭", "i": "🇮",
             "j": "🇯", "k": "🇰", "l": "🇱", "m": "🇲", "n": "🇳", "o": "🇴", "p": "🇵", "q": "🇶", "r": "🇷",
             "s": "🇸", "t": "🇹", "u": "🇺", "v": "🇻", "w": "🇼", "x": "🇽", "y": "🇾", "z": "🇿", "0": "0⃣",
             "1": "1⃣ ",
             "2": "2⃣ ", "3": "3⃣ ", "4": "4⃣ ", "5": "5⃣ ", "6": "6⃣ ", "7": "7⃣ ", "8": "8⃣ ", "9": "9⃣ ", "?": "❔",
             "!": "❕", " ": "    ", "-": "➖"}

gay_react_words = ["галя", "гей", "gay", "galya", "cleveron", "клеверон"]

tts_voices = ["alyss", "jane", "oksana", "omazh", "zahar", "ermil"]
tts_emotions = ["good", "evil", "neutral"]


def synthesize(text, voice, emotion):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

    headers = {
        'Authorization': 'Api-Key ' + os.environ.get("yandex_api_token"),
    }

    data = {
        'text': text,
        "voice": voice,
        "emotion": emotion
    }

    return requests.post(url, headers=headers, data=data)


class Module(kaizen85modules.ModuleHandler.Module):
    name = "FunStuff"
    desc = "Модуль, который добавляет бесполезные, но интересные вещи."

    async def run(self, bot: kaizen85modules.KaizenBot):
        tts_enabled = True

        if not os.path.isdir("./tts"):
            os.mkdir("./tts")

        if not os.environ.get("yandex_api_token"):
            tts_enabled = False
            print("Yandex API token is not available - TTS will not work.")

        class CommandTTE(bot.module_handler.Command):
            name = "tte"
            desc = "TextToEmoji - преобразовать буквы из текста в буквы-эмлдзи"
            args = "<text>"

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False

                string = ""
                for char in " ".join(args).strip().lower():
                    string += emojiDict[char] + " " if char in emojiDict else char + " "

                await message.channel.send(string)

                return True

        class CommandChoice(bot.module_handler.Command):
            name = "choice"
            desc = "Выбрать рандомный вариант из предоставленных"
            args = "<1, 2, 3...>"

            async def run(self, message: discord.Message, args, keys):
                choices = " ".join(message.clean_content.split()[1:]).split(", ")
                if len(choices) < 2:
                    return False

                await bot.send_info_embed(message.channel, "Я выбираю `\"%s\"`" % random.choice(choices))
                return True

        class CommandTTS(bot.module_handler.Command):
            name = "tts"
            desc = "Text To Speech"
            args = "<text> [голоса: --alyss, --jane, --oksana, --omazh] [тона: --good, --evil, --neutral]"

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False

                text = " ".join(args)
                voice = keys[0] if len(keys) > 0 and keys[0] in tts_voices else random.choice(tts_voices)
                emotion = keys[1] if len(keys) > 1 and keys[1] in tts_emotions else random.choice(tts_emotions)

                try:
                    response = synthesize(text, voice, emotion)
                except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
                    await bot.send_error_embed(message.channel, "Сервер недоступен.")
                    return True
                except requests.exceptions.ReadTimeout:
                    await bot.send_error_embed(message.channel, "Превышено время ожидания.")
                    return True

                if response.status_code != 200:
                    await bot.send_error_embed(message.channel, "Произошла ошибка\n%s" % response.text)
                    return True

                with open("./tts/%s.ogg" % message.id, "wb") as f:
                    f.write(response.content)

                with open("./tts/%s.ogg" % message.id, "rb") as f:
                    await message.channel.send("TTS voice=%s, emotion=%s (запросил: %s)" % (
                        voice, emotion,
                        message.author.mention),
                                               file=discord.File(f, filename="TTS.ogg"))

                return True

        class CommandPrntScr(bot.module_handler.Command):
            name = "prntscr"
            desc = "Рандомный скриншот с сервиса lightshot"
            args = ""

            async def run(self, message: discord.Message, args, keys):
                chars = "abcdefghijklmnopqrstuvwxyz1234567890"
                res = None

                for _ in range(5):
                    code = ""

                    for i in range(5):
                        code += chars[random.randint(1, len(chars)) - 1]

                    url = "https://prnt.sc/" + code

                    html_doc = requests.get(url,
                                            headers={"user-agent": "Mozilla/5.0 (iPad; U; CPU "
                                                                   "OS 3_2 like Mac OS X; "
                                                                   "en-us) "
                                                                   "AppleWebKit/531.21.10 ("
                                                                   "KHTML, like Gecko) "
                                                                   "Version/4.0.4 "
                                                                   "Mobile/7B334b "
                                                                   "Safari/531.21.102011-10-16 20:23:10"}).text
                    soup = BeautifulSoup(html_doc, "html.parser")

                    if not soup.find_all("img")[0]["src"].startswith("//st.prntscr.com"):
                        res = soup.find_all("img")[0]["src"]
                        break
                    else:
                        print("Not found %s" % url)

                if not res:
                    await bot.send_error_embed(message.channel, "Превышено кол-во попыток поиска изображения (5)")

                embed: discord.Embed = bot.get_info_embed(message.guild, title="Рандомное изображение с LightShot")
                embed.set_image(url=res)

                await message.channel.send(embed=embed)

                return True

        bot.module_handler.add_command(CommandTTE(), self)
        bot.module_handler.add_command(CommandChoice(), self)
        if tts_enabled:
            bot.module_handler.add_command(CommandTTS(), self)
        bot.module_handler.add_command(CommandPrntScr(), self)

    async def on_message(self, message: discord.Message, bot):
        for word in gay_react_words:
            if word in message.content.lower():
                await message.add_reaction("🏳️‍🌈")
