import asyncio

import discord

import kaizen85modules

client: kaizen85modules.KaizenBot = None
invites = {}


async def invite_update_task():
    while True:
        for guild in client.guilds:
            new_invites = await guild.invites()
            if guild.id not in invites or invites[guild.id] != new_invites:
                invites[guild.id] = new_invites

        await asyncio.sleep(2)


class Module(kaizen85modules.ModuleHandler.Module):
    kgb_messages = []

    name = "KGB"
    desc = "Секрет КГБ!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        global client
        bot.module_handler.add_param("kgbmode_enabled", True)
        bot.module_handler.add_param("custom_join_message", True)

        client = bot
        bot.module_handler.add_background_task(self, invite_update_task())

    async def on_member_remove(self, member: discord.Member, bot):
        if member.guild.system_channel:
            await bot.send_error_embed(member.guild.system_channel,
                                       "%s (%s) вышел с сервера." % (member.mention, member),
                                       "Инфо")

    async def on_member_join(self, member: discord.Member, bot):
        if member.guild.system_channel_flags.join_notifications:
            return

        inviter: discord.User

        if member.guild.id in invites:
            invites_unpacked = {}

            for invite in invites[member.guild.id]:
                invites_unpacked[invite.code] = invite

            for invite in await member.guild.invites():
                if invites_unpacked[invite.code].uses != invite.uses:
                    inviter = invite.inviter
                    break

        await bot.send_ok_embed(member.guild.system_channel,
                                "%s вошёл на сервер (пригласил: %s)." % (
                                    member.mention, inviter if inviter else "неизвестно"), title="Инфо")

        invites[member.guild.id] = await member.guild.invites()

    async def on_message_delete(self, message: discord.Message, bot: kaizen85modules.KaizenBot):
        if message.id in self.kgb_messages:
            msg = await message.channel.send(embed=message.embeds[0])
            self.kgb_messages.remove(message.id)
            self.kgb_messages.append(msg.id)
            return

        if not bot.module_handler.params["kgbmode_enabled"] or len(
                message.content) < 1:
            return

        embed = bot.get_special_embed(0x5F9EA0, "КГБ на связи!")
        embed.description = "%s удалил сообщение!" % message.author.mention
        embed.add_field(name="Сообщение:", value=message.content)

        msg = await message.channel.send(embed=embed)
        self.kgb_messages.append(msg.id)

    async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message,
                              bot: kaizen85modules.KaizenBot):
        if not bot.module_handler.params["kgbmode_enabled"] or len(
                new_message.content) < 1 or old_message.content == new_message.content:
            return

        embed = bot.get_special_embed(0x5F9EA0, "КГБ на связи!")
        embed.description = "%s изменил сообщение!" % new_message.author.mention
        embed.add_field(name="Было:", value=old_message.content)
        embed.add_field(name="Стало:", value=new_message.content)

        msg = await new_message.channel.send(embed=embed)
        self.kgb_messages.append(msg.id)
