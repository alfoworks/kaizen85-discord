import random
import discord
import kaizen85modules

emojiDict = {"a": "🇦", "b": "🇧", "c": "🇨", "d": "🇩", "e": "🇪", "f": "🇫", "g": "🇬", "h": "🇭", "i": "🇮",
             "j": "🇯", "k": "🇰", "l": "🇱", "m": "🇲", "n": "🇳", "o": "🇴", "p": "🇵", "q": "🇶", "r": "🇷",
             "s": "🇸", "t": "🇹", "u": "🇺", "v": "🇻", "w": "🇼", "x": "🇽", "y": "🇾", "z": "🇿", "0": "0⃣",
             "1": "1⃣ ",
             "2": "2⃣ ", "3": "3⃣ ", "4": "4⃣ ", "5": "5⃣ ", "6": "6⃣ ", "7": "7⃣ ", "8": "8⃣ ", "9": "9⃣ ", "?": "❔",
             "!": "❕", " ": "    ", "-": "➖"}

gay_react_words = ["галя", "гей", "gay", "galya", "cleveron", "клеверон"]


class Module(kaizen85modules.ModuleHandler.Module):
    name = "FunStuff"
    desc = "Модуль, который добавляет бесполезные, но интересные вещи."

    async def run(self, bot: kaizen85modules.KaizenBot):
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

        bot.module_handler.add_command(CommandTTE(), self)
        bot.module_handler.add_command(CommandChoice(), self)

    async def on_message(self, message: discord.Message, bot):
        for word in gay_react_words:
            if word in message.content.lower():
                await message.add_reaction("🏳️‍🌈")
