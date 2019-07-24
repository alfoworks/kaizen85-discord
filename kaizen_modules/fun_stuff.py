import os
import random

import discord
import requests

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

        bot.module_handler.add_command(CommandTTE(), self)
        bot.module_handler.add_command(CommandChoice(), self)

        if tts_enabled:
            bot.module_handler.add_command(CommandTTS(), self)

    async def on_message(self, message: discord.Message, bot):
        for word in gay_react_words:
            if word in message.content.lower():
                await message.add_reaction("🏳️‍🌈")
