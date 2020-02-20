import platform
import subprocess

import discord

import kaizen85modules

ALLOWED_USER_IDS = [337762030138163200, 327420598588276736, 308653925379211264, 287157820233875458]


class MyGlobals(dict):
    # noinspection PyMissingConstructor
    def __init__(self, globs, locs):
        self.globals = globs
        self.locals = locs

    def __getitem__(self, name):
        try:
            return self.locals[name]
        except KeyError:
            return self.globals[name]

    def __setitem__(self, name, value):
        self.globals[name] = value

    def __delitem__(self, name):
        del self.globals[name]


premade_code = """
import io
import asyncio
from contextlib import redirect_stdout
async def execute():
    out = io.StringIO()
    is_error = False
    with redirect_stdout(out):
        try:
%s
        except Exception as e:
            is_error = True
            out.write(str(e))
    if is_error:
        await bot.send_error_embed(message.channel, out.getvalue(), "Код выполнен с ошибкой")
    else:
        await bot.send_ok_embed(message.channel, out.getvalue(), "Код успешно выполнен")
asyncio.ensure_future(execute())
"""


def _exec(code: str, g, l):
    d = MyGlobals(g, l)
    code_for_embed = ""
    for line in code.splitlines(keepends=True):
        code_for_embed = code_for_embed + "            " + line
    exec(premade_code % code_for_embed, d)


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Execute"
    desc = "Позволяет выполнять Python-код прямо из сообщения!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class CommandExecute(bot.module_handler.Command):
            name = "execute"
            desc = "Выполнить Python-код из сообщения"
            args = "```Python Code```"

            async def run(self, message: discord.Message, args, keys):
                if message.author.id not in ALLOWED_USER_IDS:
                    raise bot.AccessDeniedException

                code = message.content.split("```")

                if len(code) < 3:
                    return False

                bot.logger.log("[WARN] Executing code!\n%s" % code,
                               bot.logger.PrintColors.WARNING)

                _exec(code[1].strip().rstrip(), globals(), locals())

                return True

        class CommandShell(bot.module_handler.Command):
            name = "shell"
            desc = "Выполнить консольную команду"
            args = "<команда>"

            async def run(self, message: discord.Message, args, keys):
                if message.author.id not in ALLOWED_USER_IDS:
                    raise bot.AccessDeniedException

                if len(args) < 1:
                    return False

                command = " ".join(message.content.split()[1:])

                if "shutdown" in command.lower() or "restart" in command.lower():
                    await bot.send_error_embed(message.channel,
                                               """
Использование этой команды - нарушение закона!. Закона жизни, который гласит:
Перед пацанами базар держи
Перед другом - слово.
Родителей и девушку люби, 
И храни веру перед Богом...
""")
                    return True

                bot.logger.log("[WARN] Running a shell command!\n%s" % command,
                               bot.logger.PrintColors.WARNING)

                encoding = "cp866" if platform.system() == "Windows" else "utf-8"

                try:
                    result = subprocess.check_output(command, shell=True, timeout=5, stderr=subprocess.STDOUT)
                except subprocess.TimeoutExpired:
                    await bot.send_ok_embed(message.channel, "Превышено время ожидания получения ответа команлы",
                                            "Консольная команда выполнена успешно")
                except subprocess.CalledProcessError as sex:
                    await bot.send_error_embed(message.channel, sex.output.decode(encoding),
                                               "Не удалось выполнить консольную команду")
                else:
                    await bot.send_ok_embed(message.channel, result.decode(encoding), "Консольная команда выполнена")

                return True

        bot.module_handler.add_command(CommandExecute(), self)
        bot.module_handler.add_command(CommandShell(), self)
