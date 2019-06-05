import asyncio
import os
import pickle
from collections import Awaitable
from typing import List

import discord


class Logger:
    class PrintColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    def log(self, text, color=PrintColors.ENDC):
        print(color + text + self.PrintColors.ENDC)


class KaizenBot(discord.Client):
    CMD_PREFIX = "!"
    BOT_NAME = "Kaizen-85"
    GLOBAL_GUILD_LOCK = None
    EMOJI_OK = "☑"
    EMOJI_ERR = "🛑"
    EMOJI_WARN = "⚠"

    start_time = 0

    module_handler = None
    logger = Logger()

    def load_modules(self):
        pass

    def run_modules(self):
        pass

    def get_special_embed(self, color=0xFFFFFF, title="Embed") -> discord.Embed:
        embed = discord.Embed(color=color)
        embed.set_author(name=title, icon_url=self.user.avatar_url)

        return embed

    async def send_info_embed(self, channel: discord.TextChannel, text: str = None, title: str = "Инфо"):
        role = channel.guild.me.top_role
        color = 0xb63a6b

        if role:
            color = role.color.value

        embed = self.get_special_embed(title=title, color=color)
        embed.description = text

        await channel.send(embed=embed)

    async def send_error_embed(self, channel: discord.TextChannel, text: str = None, title: str = "Ошибка"):
        embed = self.get_special_embed(0xFF4C4C, title=title)
        embed.description = text

        await channel.send(embed=embed)

    async def send_ok_embed(self, channel: discord.TextChannel, text: str = None, title: str = "ОК"):
        embed = self.get_special_embed(0x6AAF6A, title=title)
        embed.description = text

        await channel.send(embed=embed)

    def get_info_embed(self, guild: discord.Guild, text: str = None, title: str = "Инфо"):
        role = guild.me.top_role
        color = 0xb63a6b

        if role:
            color = role.color.value

        embed = self.get_special_embed(title=title, color=color)
        embed.description = text

        return embed

    def get_error_embed(self, text: str = None, title: str = "Ошибка"):
        embed = self.get_special_embed(0xFF4C4C, title=title)
        embed.description = text

        return embed

    def get_ok_embed(self, text: str = None, title: str = "ОК"):
        embed = self.get_special_embed(0x6AAF6A, title=title)
        embed.description = text

        return embed

    @staticmethod
    def check_permissions(member_perms: discord.Permissions, perms_list) -> bool:
        if len(perms_list) < 1:
            return True

        member_perms_dict = {}

        for k, v in iter(member_perms):
            member_perms_dict[k] = v

        for perm in perms_list:
            if not member_perms_dict[perm]:
                return False

        return True

    class AccessDeniedException(Exception):
        def __init__(self):
            super().__init__("AccessDenied")


class ModuleHandler:
    modules = {}
    tasks = {}
    commands = {}
    params = {"test": "test"}

    PARAMS_FILE = "kaizen_params.pkl"

    class Module:
        name = "module"
        desc = "..."

        async def run(self, bot: KaizenBot):
            pass

        def on_unload(self):
            pass

        """
        Ивенты дискорда.
        Дабы не было вопросов скажу, что это сделано для того, 
        чтобы один модуль не смог заместить ивент другого модуля или основы бота
        (kaizen85core), так уж работает @client.event.
        """

        # TODO: если будет скучно, то можно добавить приведение типов.

        async def on_message(self, message: discord.Message, bot: KaizenBot):
            pass

        async def on_message_delete(self, message: discord.Message, bot: KaizenBot):
            pass

        async def on_message_edit(self, old_message: discord.Message, new_message: discord.Message, bot: KaizenBot):
            pass

        async def on_member_remove(self, member: discord.Member, bot: KaizenBot):
            pass

        async def on_disconnect(self, bot: KaizenBot):
            pass

        async def on_resumed(self, bot: KaizenBot):
            pass

        async def on_error(self, event, bot: KaizenBot, *args, **kwargs):
            pass

        async def on_socket_raw_receive(self, msg, bot: KaizenBot):
            pass

        async def on_socket_raw_send(self, payload, bot: KaizenBot):
            pass

        async def on_typing(self, channel, user, when, bot: KaizenBot):
            pass

        async def on_bulk_message_delete(self, messages, bot: KaizenBot):
            pass

        async def on_raw_message_delete(self, payload, bot: KaizenBot):
            pass

        async def on_raw_bulk_message_delete(self, payload, bot: KaizenBot):
            pass

        async def on_raw_message_edit(self, payload, bot: KaizenBot):
            pass

        async def on_reaction_add(self, reaction, user, bot: KaizenBot):
            pass

        async def on_raw_reaction_add(self, payload, bot: KaizenBot):
            pass

        async def on_reaction_remove(self, reaction, user, bot: KaizenBot):
            pass

        async def on_raw_reaction_remove(self, payload, bot: KaizenBot):
            pass

        async def on_reaction_clear(self, message, reactions, bot: KaizenBot):
            pass

        async def on_raw_reaction_clear(self, payload, bot: KaizenBot):
            pass

        async def on_private_channel_delete(self, channel, bot: KaizenBot):
            pass

        async def on_private_channel_create(self, channel, bot: KaizenBot):
            pass

        async def on_private_channel_update(self, before, after, bot: KaizenBot):
            pass

        async def on_private_channel_pins_update(self, channel, last_pin, bot: KaizenBot):
            pass

        async def on_guild_channel_delete(self, channel, bot: KaizenBot):
            pass

        async def on_guild_channel_create(self, channel, bot: KaizenBot):
            pass

        async def on_guild_channel_update(self, before, after, bot: KaizenBot):
            pass

        async def on_guild_channel_pins_update(self, channel, last_pin, bot: KaizenBot):
            pass

        async def on_guild_integrations_update(self, guild, bot: KaizenBot):
            pass

        async def on_webhooks_update(self, channel, bot: KaizenBot):
            pass

        async def on_member_join(self, member, bot: KaizenBot):
            pass

        async def on_member_update(self, before, after, bot: KaizenBot):
            pass

        async def on_user_update(self, before, after, bot: KaizenBot):
            pass

        async def on_guild_join(self, guild, bot: KaizenBot):
            pass

        async def on_guild_remove(self, guild, bot: KaizenBot):
            pass

        async def on_guild_update(self, before, after, bot: KaizenBot):
            pass

        async def on_guild_role_create(self, role, bot: KaizenBot):
            pass

        async def on_guild_role_delete(self, role, bot: KaizenBot):
            pass

        async def on_guild_role_update(self, before, after, bot: KaizenBot):
            pass

        async def on_guild_emojis_update(self, guild, before, after, bot: KaizenBot):
            pass

        async def on_guild_available(self, guild, bot: KaizenBot):
            pass

        async def on_guild_unavailable(self, guild, bot: KaizenBot):
            pass

        async def on_voice_state_update(self, member, before, after, bot: KaizenBot):
            pass

        async def on_member_ban(self, guild, user, bot: KaizenBot):
            pass

        async def on_member_unban(self, guild, user, bot: KaizenBot):
            pass

        async def on_group_join(self, channel, user, bot: KaizenBot):
            pass

        async def on_group_remove(self, channel, user, bot: KaizenBot):
            pass

        async def on_relationship_add(self, relationship, bot: KaizenBot):
            pass

        async def on_relationship_remove(self, relationship, bot: KaizenBot):
            pass

        async def on_relationship_update(self, before, after, bot: KaizenBot):
            pass

    class Command:
        name = "command"
        desc = "..."
        args = "..."
        keys = []

        permissions = []

        module = None

        async def run(self, message: discord.Message, args: str, keys: List[str]) -> bool:
            return True

    # ======= MODULES

    def add_module(self, module: Module):
        if module.name in self.modules:
            raise ValueError("A module with name \"%s\" already exists." % module.name)

        self.modules[module.name] = module
        self.tasks[module.name] = []

    def unload_module(self, module_name: str):
        if module_name not in self.modules:
            raise ValueError("Can't remove a module that doesn't exist (%s)." % module_name)

        print("Unloading module \"%s\"..." % module_name)

        self.modules[module_name].on_unload()

        for _, command in list(self.commands.items()):
            if command.module.name == module_name:
                self.remove_command(command.name)

                print("Removed command \"%s\" from module \"%s\"." % (command.name, module_name))

        for task in self.tasks[module_name]:
            task.cancel()

            print("Cancelled task from module \"%s\"." % module_name)

        del self.modules[module_name]

    # ======= BACKGROUND TASKS

    def add_background_task(self, module: Module, coro: Awaitable):
        self.tasks[module.name].append(asyncio.get_event_loop().create_task(coro))

    # ======= COMMANDS

    def add_command(self, command: Command, module: Module):
        command.module = module
        self.commands[command.name] = command

    def remove_command(self, command_name: str):
        if command_name not in self.commands:
            raise ValueError("Can't remove a module that doesn't exist (%s)." % command_name)

        del self.commands[command_name]

    # ======= PARAMS

    def save_params(self):
        with open(self.PARAMS_FILE, "wb") as f:
            pickle.dump(self.params, f)

    def load_params(self):
        if not os.path.isfile(self.PARAMS_FILE):
            self.save_params()
        else:
            with open(self.PARAMS_FILE, "rb") as f:
                self.params = pickle.load(f)

    def add_param(self, key, value_default):
        if key not in self.params:
            self.params[key] = value_default

            self.save_params()
