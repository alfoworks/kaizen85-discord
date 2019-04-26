import discord
import kaizen85modules


class Module(kaizen85modules.ModuleHandler.Module):
    MAIN_CHANNEL = 394132322372419597

    name = "KGB"
    desc = "Секрет КГБ!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        bot.module_handler.add_param("kgbmode_enabled", True)

    async def on_member_remove(self, member: discord.Member, bot):
        await bot.send_error_embed(member.guild.get_channel(self.MAIN_CHANNEL), "%s вышел с сервера." % member.mention,
                                   "Инфо")

    async def on_message_delete(self, message: discord.Message, bot: kaizen85modules.KaizenBot):
        if not bot.module_handler.params["kgbmode_enabled"] or len(
                message.content) < 1 or message.author.guild_permissions.administrator:
            return

        embed = bot.get_special_embed(0x5F9EA0, "КГБ на связи!")
        embed.description = "%s удалил сообщение!" % message.author.mention
        embed.add_field(name="Сообщение:", value=message.content)

        await message.channel.send(embed=embed)

    async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message,
                              bot: kaizen85modules.KaizenBot):
        if not bot.module_handler.params["kgbmode_enabled"] or len(
                new_message.content) < 1 or old_message.content == new_message.content\
                or new_message.author.guild_permissions.administrator:
            return

        embed = bot.get_special_embed(0x5F9EA0, "КГБ на связи!")
        embed.description = "%s изменил сообщение!" % new_message.author.mention
        embed.add_field(name="Было:", value=old_message.content)
        embed.add_field(name="Стало:", value=new_message.content)

        await new_message.channel.send(embed=embed)
