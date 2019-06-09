import math
import os
import random
import time
import traceback
from os import path

import discord

import kaizen85modules


class Bot(kaizen85modules.KaizenBot):
    MODULES_DIR = "kaizen_modules"
    GLOBAL_GUILD_LOCK = 394132321839874050
    ACCESS_DENIED_MSGS = ["Прав не завезли!", "Нойра бы такого не одобрил...",
                          "Увы, но ты слишком мелковат для этого...", "Вы точно уверены? (да/нет)", "Ошибка 403",
                          "Действие не выполнено, не знаю, почему.", "Под админа косишь?"]

    module_handler = kaizen85modules.ModuleHandler()

    def load_modules(self):
        for file in os.listdir(self.MODULES_DIR):
            if file.endswith(".py"):
                module = __import__("%s.%s" % (self.MODULES_DIR, file[:-3]), globals(), locals(),
                                    fromlist=["Module"]).Module()
                self.module_handler.add_module(module)

                self.logger.log("Loaded module \"%s\"" % module.name, self.logger.PrintColors.OKBLUE)

        self.module_handler.add_module(BaseModule())

    async def run_modules(self):
        self.logger.log("\nRunning modules...", self.logger.PrintColors.WARNING)
        for _, mod in self.module_handler.modules.items():
            await mod.run(self)


class BaseModule(kaizen85modules.ModuleHandler.Module):
    name = "BaseModule"
    desc = "Встроенный модуль с базовыми функциями."

    @staticmethod
    def parse_value(value, value_type):
        if value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        elif value_type == bool:
            if value.lower() == "true" or value.lower() == "yes":
                return True
            elif value.lower() == "false" or value.lower() == "no":
                return False
        elif value_type == str:
            return value
        else:
            return None

    async def run(self, bot):
        class CommandModules(bot.module_handler.Command):
            name = "modules"
            desc = "Информация о модулях и управление ими."
            args = "[reload/cmds] [имя модуля]"

            async def run(self, message, args, keys):
                if len(args) > 0 and args[0] == "reload":
                    if not bot.check_permissions(message.author.guild_permissions, ["administrator"]):
                        raise bot.AccessDeniedException()

                    for name, _ in list(bot.module_handler.modules.items()):
                        bot.module_handler.unload_module(name)

                    bot.load_modules()
                    await bot.run_modules()
                    return True
                elif len(args) > 1 and args[0] == "cmds":
                    module_name = " ".join(args[2:]).lower()

                    for _, mod in list(bot.module_handler.modules.items()):
                        if mod.name.lower() == module_name:
                            embed: discord.Embed = bot.get_info_embed(message.guild,
                                                                      title="Список команд модуля %s" % mod.name)
                            for _, command in bot.module_handler.commands.items():
                                if command.module == mod:
                                    keys_user = []
                                    for key in command.keys:
                                        keys_user.append("[--%s]" % key)

                                    embed.add_field(
                                        name="%s%s %s %s" % (
                                            bot.CMD_PREFIX, command.name, command.args, " ".join(keys_user)),
                                        value=command.desc, inline=False)

                            await message.channel.send(embed=embed)

                            return True

                    await bot.send_error_embed(message.channel, "Модуль с таким именем не найден!")
                    return True

                embed: discord.Embed = bot.get_info_embed(message.guild, title="Список модулей")

                embed.description = "Всего модулей: %s." % len(bot.module_handler.modules)

                for _, mod in list(bot.module_handler.modules.items()):
                    embed.add_field(name=mod.name, value=mod.desc, inline=False)

                await message.channel.send(embed=embed)
                return True

        class CommandCmds(bot.module_handler.Command):
            name = "cmds"
            desc = "Список команд, их аргументы и описание."
            keys = ["all"]

            async def run(self, message, args, keys):
                embed: discord.Embed = bot.get_info_embed(message.guild, title="Список команд")

                for _, command in bot.module_handler.commands.items():
                    if "all" in keys or bot.check_permissions(message.author.guild_permissions, command.permissions):
                        keys_user = []
                        for key in command.keys:
                            keys_user.append("[--%s]" % key)

                        embed.add_field(
                            name="%s%s %s %s" % (bot.CMD_PREFIX, command.name, command.args, " ".join(keys_user)),
                            value=command.desc, inline=False)

                embed.description = "Всего команд: %s, доступных вам: %s." % (len(bot.module_handler.commands), len(
                    list(filter(lambda cmd: bot.check_permissions(message.author.guild_permissions,
                                                                  bot.module_handler.commands[cmd].permissions),
                                bot.module_handler.commands))))

                await message.channel.send(embed=embed)
                return True

        class CommandDie(bot.module_handler.Command):
            name = "die"
            desc = "Выключить бота"
            permissions = ["administrator"]

            async def run(self, message, args, keys):
                try:
                    bot.loop.run_until_complete(bot.logout())
                except Exception:
                    pass

                return True

        class CommandParams(bot.module_handler.Command):
            name = "params"
            desc = "Список параметров и управление ими"
            args = "[set] [key] [value]"
            permissions = ["administrator"]

            async def run(self, message, args, keys):
                if len(args) >= 3 and args[0] == "set":
                    if args[1] not in bot.module_handler.params:
                        await bot.send_error_embed(message.channel, "Параметр с таким именем не найден.")

                        return True

                    param = bot.module_handler.params[args[1]]
                    try:
                        val = BaseModule.parse_value(" ".join(args[2:]), type(param))
                    except ValueError:
                        await bot.send_error_embed(message.channel,
                                                   "Неподходящее для типа \"%s\" значение." % type(param).__name__)

                        return True

                    if val is None:
                        await bot.send_error_embed(message.channel,
                                                   "Параметр \"%s\" нелья изменить с помощью команды." % args[1])
                        return True

                    bot.module_handler.params[args[1]] = val
                    bot.module_handler.save_params()

                    return True

                embed: discord.Embed = bot.get_info_embed(message.guild, title="Список параметров")

                for k, v in bot.module_handler.params.items():
                    embed.add_field(name="%s [%s]" % (k, type(v).__name__), value=v, inline=False)

                await message.channel.send(embed=embed)

                return True

        bot.module_handler.add_command(CommandModules(), self)
        bot.module_handler.add_command(CommandCmds(), self)
        bot.module_handler.add_command(CommandDie(), self)
        bot.module_handler.add_command(CommandParams(), self)


start_loading_time = time.time()

client = Bot()

# ==================================================== #

client.logger.log("Loading modules...\n", client.logger.PrintColors.WARNING)

if not path.isdir(client.MODULES_DIR):
    os.mkdir(client.MODULES_DIR)

client.load_modules()

client.logger.log("\nLogging into Discord...", client.logger.PrintColors.WARNING)


@client.event
async def on_ready():
    client.logger.log("Logged into Discord as \"%s\"." % client.user.name, client.logger.PrintColors.WARNING)

    client.logger.log("Loading params...", client.logger.PrintColors.WARNING)
    client.module_handler.load_params()

    await client.run_modules()

    client.start_time = time.time()

    client.logger.log("""
==============
INIT FINISHED! (took %ss)
Loaded Modules: %s
Loaded Commands: %s
Loaded Params: %s
==============
    """ % (math.floor(time.time() - start_loading_time), len(client.module_handler.modules),
           len(client.module_handler.commands), len(client.module_handler.params)),
                      client.logger.PrintColors.OKBLUE)


@client.event
async def on_message(message: discord.Message):
    # ==== Modules
    for _, mod in list(client.module_handler.modules.items()):
        await mod.on_message(message, client)

    # ==== Commands
    if not message.content.startswith(client.CMD_PREFIX):
        return

    if type(message.channel) is not discord.TextChannel:
        await message.channel.send("Бот работает только на серверах!")
        return
    elif client.GLOBAL_GUILD_LOCK and message.channel.guild.id != client.GLOBAL_GUILD_LOCK:
        await client.send_error_embed(message.channel, "Данный бот не работает на этом сервере!", "Guild-Lock")
        return

    args = message.content.split()
    cmd = args.pop(0)[len(client.CMD_PREFIX):].lower()

    if cmd not in client.module_handler.commands:
        await client.send_error_embed(message.channel, "Ты %s" % message.clean_content[1:], "Команда не найдена")
        return

    command: client.module_handler.Command = client.module_handler.commands[cmd]

    keys = []
    for arg in args:
        if arg.startswith("--") and len(arg) > 2 and arg not in keys:
            keys.append(arg)

    for i, key in enumerate(keys):
        args.remove(key)
        keys[i] = key[2:]

    if not client.check_permissions(message.author.guild_permissions, command.permissions):
        await client.send_error_embed(message.channel, random.choice(client.ACCESS_DENIED_MSGS), "Нет прав!")
        return

    # noinspection PyBroadException
    try:
        ok = await command.run(message, args, keys)
    except discord.Forbidden:
        await client.send_error_embed(message.channel, "У бота нет прав!")
    except client.AccessDeniedException:
        await client.send_error_embed(message.channel, random.choice(client.ACCESS_DENIED_MSGS), "Нет прав!")
    except Exception:
        await client.send_error_embed(message.channel, "```\n%s\n```" % traceback.format_exc(),
                                      "⚠️ Криворукий уебан, у тебя ошибка! ⚠️")
    else:
        if not ok:
            keys_user = []
            for key in command.keys:
                keys_user.append("[--%s]" % key)

            embed: discord.Embed = client.get_error_embed(title="Недостаточно аргументов!")
            embed.add_field(name="%s%s %s %s" % (client.CMD_PREFIX, command.name, command.args, " ".join(keys_user)),
                            value=command.desc)

            await message.channel.send(embed=embed)

            try:
                await message.add_reaction(client.EMOJI_ERR)
            except discord.NotFound:
                pass
        else:
            try:
                await message.add_reaction(client.EMOJI_OK)
            except discord.NotFound:
                pass


@client.event
async def on_message_delete(message: discord.Message):
    for _, mod in list(client.module_handler.modules.items()):
        await mod.on_message_delete(message, client)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    for _, mod in list(client.module_handler.modules.items()):
        await mod.on_message_edit(before, after, client)


@client.event
async def on_member_remove(member: discord.Member):
    for _, mod in list(client.module_handler.modules.items()):
        await mod.on_member_remove(member, client)


# TODO: добавить все остальные ивенты дискорда для модулей, по анадогии с тем, что выше. Чисто работа ручками.


# ==================================================== #

client.run(os.environ.get("kaizen85_token"))
