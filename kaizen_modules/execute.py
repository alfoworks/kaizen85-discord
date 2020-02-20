import discord

import kaizen85modules


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
        if len(out.getvalue()) <= 2048:
            await bot.send_ok_embed(message.channel, out.getvalue(), "Код успешно выполнен")
        else:
            await bot.send_ok_embed(message.channel, "Размер вывода превышает 2048 символов", "Код успешно выполнен")
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
            permissions = ["administrator"]

            async def run(self, message: discord.Message, args, keys):
                code = message.content.split("```")
                bot.logger.log("Executing code. It's necessary to use bot object for right executing",
                               bot.logger.PrintColors.WARNING)
                if len(code) < 3:
                    return False
                _exec(code[1].strip().rstrip(), globals(), locals())

                return True

        bot.module_handler.add_command(CommandExecute(), self)
