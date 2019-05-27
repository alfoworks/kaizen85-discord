import urllib.parse
import urllib.request

import discord
from bs4 import BeautifulSoup

import kaizen85modules


class Module(kaizen85modules.ModuleHandler.Module):
    name = "YoutubeSearch"
    desc = "Поиск видео в YouTube"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class CommandYT(bot.module_handler.Command):
            name = "yt"
            desc = "Поиск на YouTube"
            args = "<поисковый запрос>"
            permissions = []

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False

                keyword = " ".join(message.clean_content.split()[1:])

                url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(keyword)
                response = urllib.request.urlopen(url)
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')

                vids = []

                for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
                    vid_url = "https://www.youtube.com" + vid["href"]

                    if "channel" not in vid_url:
                        vids.append(vid_url)

                if len(vids) < 1:
                    await bot.send_error_embed(message.channel, "Видео по запросу %s не найдено!" % keyword)
                    return True

                await message.channel.send(
                    "Видео по запросу \"%s\": (запросил: %s)\n%s" % (keyword, message.author.mention, vids[0]))

                return True

        bot.module_handler.add_command(CommandYT(), self)
