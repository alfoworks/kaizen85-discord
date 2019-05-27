import os

import discord
from google_images_download import google_images_download
from nudenet import NudeDetector

import kaizen85modules

detector_model = "detector_model"


class Module(kaizen85modules.ModuleHandler.Module):
    name = "ImageSearch"
    desc = "Поиск картинок в Google с автоматическим помещением в спойлер при обнаружении NSFW."

    async def run(self, bot: kaizen85modules.KaizenBot):
        detector = None

        if not os.path.isfile(detector_model):
            bot.logger.log("[ImageSearch] Can't find detector model file. NSFW check will not work.")
        else:
            detector = NudeDetector(detector_model)

        class CommandImg(bot.module_handler.Command):
            name = "img"
            desc = "Поиск изображений в Google"
            args = "<поисковый запрос>"
            keys = ["no-nsfw-check"]

            async def run(self, message: discord.Message, args, keys):
                if len(args) < 1:
                    return False

                keyword = " ".join(message.clean_content.split()[1:])

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
                global is_nsfw
                is_nsfw = False

                # noinspection PyBroadException
                try:
                    if not ("no-nsfw-check" in keys
                            and bot.check_permissions(message.author.guild_permissions, ["administrator"]))\
                            and detector is not None:
                        is_nsfw = True if len(detector.detect(img_path)) > 0 else False
                except Exception:
                    pass

                with open(img_path, "rb") as f:
                    img = discord.File(f, spoiler=is_nsfw)

                    await message.channel.send("Картинка по запросу \"%s\": (запросил: %s)%s%s" % (
                        keyword, message.author.mention,
                        "\n⚠️Обнаружен NSFW контент! Картинка спрятана под спойлер. Открывайте на свой страх и риск! ⚠️" if is_nsfw else "", "\n⚠️Проверка NSFW отключена! Проверьте логи. ⚠️" if not detector else ""),
                                               file=img)

                return True

        bot.module_handler.add_command(CommandImg(), self)
