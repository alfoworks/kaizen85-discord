import asyncio
import io
from contextlib import redirect_stdout
import discord
import kaizen85modules


class MyGlobals(dict):
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


def _exec(code, g, l):
    out = io.StringIO()
    d = MyGlobals(g, l)
    try:
        error = False
        with redirect_stdout(out):
            exec(code, d)
    except Exception as ex:
        error = True
        out.write(str(ex))

    return out.getvalue(), error


def _await(coro):  # це костыль для выполнения асинхронных функций в exec
    asyncio.ensure_future(coro)


class Module(kaizen85modules.ModuleHandler.Module):
    name = "Execute"
    desc = "Позволяет выполнять Python-код прямо из сообщения!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class CommandExecute(bot.module_handler.Command):
            name = "execute"
            desc = "Выполнить Python-код из сообщения"
            args = "```Python Code```"
            permissions = ["administrator"]

            async def run(self, message: discord.Message, args: str, keys):
                code = message.content.split("```")

                if len(code) < 3:
                    return False

                out, is_error = _exec(code[1].strip().rstrip(), globals(), locals())

                if is_error:
                    await bot.send_error_embed(message.channel, out, "Код выполнен с ошибкой")
                else:
                    await bot.send_ok_embed(message.channel, out, "Код успешно выполнен")

                return True

        bot.module_handler.add_command(CommandExecute(), self)
