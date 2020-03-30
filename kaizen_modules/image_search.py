import os

import discord
import requests
from nudenet import NudeDetector

import kaizen85modules

detector_model = "detector_model"
request_url = "https://www.googleapis.com/customsearch/v1?q=%s&num=1&start=1" \
              "&searchType=image&key=%s&cx=%s"


class Module(kaizen85modules.ModuleHandler.Module):
    name = "ImageSearch"
    desc = "Поиск картинок в Google с автоматическим помещением в спойлер при обнаружении NSFW (и цензурированием в " \
           "не NSFW каналах). "

    async def run(self, bot: kaizen85modules.KaizenBot):
        detector = None

        if not os.path.isfile(detector_model):
            bot.logger.log("[ImageSearch] Can't find detector model file. NSFW check will not work.")
        else:
            detector = NudeDetector(detector_model)

        cx = os.environ.get("kaizen_image_search_cx")
        api_key = os.environ.get("kaizen_image_search_apikey")

        if cx is None or api_key is None:
            bot.logger.log("[ImageSearch] CX or API key are not available. Check \"kaizen_image_search_cx\" amd "
                           "\"kaizen_image_search_apikey\" in PATH.")

        class CommandImg(bot.module_handler.Command):
            name = "img"
            desc = "Поиск изображений в Google"
            args = "<поисковый запрос>"
            keys = ["no-nsfw-check"]

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False

                keyword = " ".join(message.clean_content.split()[1:])

                """
                 resp = google_images_download.googleimagesdownload()
                aip = resp.download(arguments={"keywords": keyword, "limit": 1, "output_directory": "img_search",
                                               "no_directory": True})

                if len(aip[next(iter(aip))]) < 1:
                    await bot.send_error_embed(message.channel, "%s, изображение по запросу \"%s\" не найдено!" % (
                        message.author.mention, keyword))
                    return True

                img_path = aip[next(iter(aip))][0]

                if len(img_path) < 1:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при загрузке картинки по запросу \"%s\"!" % (
                                                   message.author.mention, keyword))
                    return True
                """

                try:
                    resp = requests.get(request_url % (keyword, api_key, cx))
                except Exception:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при загрузке картинки по запросу \"%s\"!" % (
                                                   message.author.mention, keyword))
                    return True

                if resp.status_code != 200:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при загрузке картинки по запросу \"%s\": %s" % (
                                                   message.author.mention, keyword, resp.text))
                    return True

                data = resp.json()
                if data["searchInformation"]["totalResults"] == "0":
                    await bot.send_error_embed(message.channel, "%s, изображение по запросу \"%s\" не найдено!" % (
                        message.author.mention, keyword))
                    return True

                img_path = "./img_search/%s.%s" % (message.id, data["items"][0]["fileFormat"].split("/")[-1])

                try:
                    with open(img_path, "wb") as f:
                        f.write(requests.get(data["items"][0]["link"]).content)
                except Exception:
                    await bot.send_error_embed(message.channel,
                                               "%s, произошла ошибка при скачивании картинки по запросу \"%s\"!" % (
                                                   message.author.mention, keyword))
                    return True

                global is_nsfw
                is_nsfw = False

                # noinspection PyBroadException
                try:
                    if not ("no-nsfw-check" in keys
                            and bot.check_permissions(message.author.guild_permissions, ["administrator"])) \
                            and detector is not None:
                        is_nsfw = True if len(detector.detect(img_path)) > 0 else False
                except Exception:
                    pass

                if is_nsfw and not message.channel.is_nsfw():
                    detector.censor(img_path, out_path=img_path, visualize=False)

                with open(img_path, "rb") as f:
                    img = discord.File(f, spoiler=is_nsfw)

                    await message.channel.send("Картинка по запросу \"%s\": (запросил: %s)%s%s" % (
                        keyword, message.author.mention,
                        "\n⚠️Обнаружен NSFW контент! Картинка спрятана под спойлер. Открывайте на свой страх и риск! ⚠️" if is_nsfw else "",
                        "\n⚠️Проверка NSFW отключена! Проверьте логи. ⚠️" if not detector else ""),
                                               file=img)

                return True

        bot.module_handler.add_command(CommandImg(), self)
