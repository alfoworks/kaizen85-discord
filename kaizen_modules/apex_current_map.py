import asyncio
import time

import discord

import kaizen85modules

maps = ["World's Edge", "Kings Canyon", "Kings Canyon After Dark"]

# MAPS = {
#     "World's Edge": 5400,
#     "Kings Canyon": 5400,
#     "Kings Canyon After Dark": 1800
# }


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


async def udp_info(channel_id: int, bot: kaizen85modules.KaizenBot):
    while True:
        channel: discord.TextChannel= bot.get_channel(channel_id)

        if not channel:
            print("[ApexCurrentMap] Wrong channel id!")
            break
        cycle = ((time.time() + 10800) % (5400+5400+1800)) // 5400
        descript = "Текущая карта: " + " | ".join(["__**%s**__" % e if i == cycle else  e for i, e in enumerate(maps)])
        await channel.edit(topic=descript)
        await asyncio.sleep(60)


class Module(kaizen85modules.ModuleHandler.Module):
    name = "ApexCurrentMap"
    desc = "Показывает текущую карту Apex Legends в описании канала"

    async def run(self, bot):
        bot.module_handler.add_param("apex_channel_id", 0)
        channel_id = bot.module_handler.params["apex_channel_id"]

        if channel_id != 0:
            bot.module_handler.add_background_task(self, udp_info(channel_id, bot))
            print("[ApexCurrentMap] Started channel update task!")
