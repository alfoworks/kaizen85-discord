import threading

import discord
import requests
from bs4 import BeautifulSoup

import kaizen85modules

service_url = "https://alekssamosbt.ru/vision/index.php"


def image_scan(message, url, bot):  # Да-да, говнокод.
    request = requests.post(service_url, data={"userlink": url})

    soup = BeautifulSoup(request.text, "html.parser")
    results = soup.find_all("div", {"class": "success description"})

    if not len(results):
        bot.loop.create_task(bot.send_error_embed(message.channel, "Произошла ошибка сервиса."))

        return True

    embed: discord.Embed = bot.get_info_embed(message.guild, results[0].text,
                                              "Результат распознавания")
    embed.set_image(url=url)

    bot.loop.create_task(message.channel.send(embed=embed))


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Vision"
    desc = "Распознавание объектов с картинки, примерное описание"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class CommandVs(bot.module_handler.Command):
            name = "vs"
            desc = "Распознавание объектов с картинки, примерное описание"
            args = "<картинка>"

            async def run(self, message: discord.Message, args, keys):
                if not len(message.attachments):
                    return False

                attachment = message.attachments[0]

                if not attachment.filename.lower().endswith(("jpg", "gif", "png")):
                    await bot.send_error_embed(message.channel, "Данный тип файла не поддерживается сервисом.")

                    return True

                await message.add_reaction("⏳")

                threading.Thread(target=image_scan, args=[message, attachment.url, bot]).start()

                return True

        bot.module_handler.add_command(CommandVs(), self)
