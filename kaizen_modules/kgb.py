import discord
import kaizen85modules


class Module(kaizen85modules.ModuleHandler.Module):
    MAIN_CHANNEL = 394132322372419597
    kgb_messages = []

    name = "KGB"
    desc = "Секрет КГБ!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        bot.module_handler.add_param("kgbmode_enabled", True)

    async def on_member_remove(self, member: discord.Member, bot):
        await bot.send_error_embed(member.guild.get_channel(self.MAIN_CHANNEL), "%s вышел с сервера." % member.mention,
                                   "Инфо")

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
