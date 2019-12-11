import asyncio
import time
import discord
import kaizen85modules

client: kaizen85modules.KaizenBot = None
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


def pluralize_russian(number, nom_sing, gen_sing, gen_pl):
    s_last_digit = str(number)[-1]

    if int(str(number)[-2:]) in range(11, 20):
        # 11-19
        return gen_pl
    elif s_last_digit == '1':
        # 1
        return nom_sing
    elif int(s_last_digit) in range(2, 5):
        # 2,3,4
        return gen_sing
    else:
        # 5,6,7,8,9,0
        return gen_pl


async def upd_presence():
    while True:
        secs = time.time() - client.start_time

        days = round(secs // 86400)
        hours = round((secs - days * 86400) // 3600)
        minutes = round((secs - days * 86400 - hours * 3600) // 60)
        seconds = round(secs - days * 86400 - hours * 3600 - minutes * 60)

        days_text = pluralize_russian(days, "день", "дня", "дней")
        hours_text = pluralize_russian(hours, "час", "часа", "часов")
        minutes_text = pluralize_russian(minutes, "минута", "минуты", "минут")
        seconds_text = pluralize_russian(seconds, "секунда", "секунды", "секунд")

        uptime = ", ".join(filter(lambda x: bool(x), ["{0} {1}".format(days, days_text) if days else "",
                                                      "{0} {1}".format(hours, hours_text) if hours else "",
                                                      "{0} {1}".format(minutes, minutes_text) if minutes else "",
                                                      "{0} {1}".format(seconds, seconds_text) if seconds else ""]))

        await client.change_presence(
            activity=discord.Streaming(name="Аптайм: %s" % uptime, url="https://twitch.tv/allformine"))

        await asyncio.sleep(5)


class Module(kaizen85modules.ModuleHandler.Module):
    name = "BotUptimePresence"
    desc = "Показывает аптайм бота в Discord"

    async def run(self, bot):
        global client
        client = bot

        bot.module_handler.add_background_task(self, upd_presence())

        print("[BotUptimePresence] Started presence update task!")
