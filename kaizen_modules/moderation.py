import discord
import kaizen85modules


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


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Moderation"
    desc = "Полезные команды для модерации"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class CommandPurge(bot.module_handler.Command):
            name = "purge"
            desc = "Удалить большое кол-во сообщений."
            args = "<1 - 100> [@пользователь]"
            permissions = ["manage_messages"]

            async def run(self, message: discord.Message, args: str, keys):
                if len(args) < 1:
                    return False

                try:
                    limit = int(args[0])
                except ValueError:
                    return False

                if limit < 1 or limit > 100:
                    return False

                def check(msg):
                    return True if len(message.mentions) < 1 else msg.author == message.mentions[0]

                await message.delete()

                deleted = await message.channel.purge(limit=limit, check=check)
                await bot.send_ok_embed(message.channel, "%s: Удалено %s %s." % (message.author.mention, len(deleted),
                                                                                 pluralize_russian(len(deleted),
                                                                                                   "сообщение",
                                                                                                   "сообщения",
                                                                                                   "сообщений")))

                return True

        bot.module_handler.add_command(CommandPurge(), self)
