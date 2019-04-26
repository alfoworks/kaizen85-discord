from typing import List
import discord
import kaizen85modules

"""
async def background():
    print("test")
    asyncio.sleep(5)
"""


class Module(kaizen85modules.ModuleHandler.Module):
    name = "DummyModule"  # имя модуля
    desc = "Протести моё очко, командир!"  # описание модуля

    # главный метод модуля, который выполняется когда бот подключился к Discord
    async def run(self, bot: kaizen85modules.KaizenBot):  # создание команжы
        """
        #==Примеры использования функций бота==#

         bot.module_handler.add_paramz("test_param", "anus") # Це система параметров
         бота. Каждый модуль должен выполнять эту функцию для кажлого параметра.
         Она записывает ключ и стандартное значение, если ключ еще не записан. В противном
         случае она не делает ничего, т.е. с уже записанным параметром ничего не произойдет

         Изменять параметр нужно так:
         bot.module_handler.params["key"] = value
         bot.module_handler.save_params()

         #=====================================#

         bot.module_handler.add_background_task(self, background())

         Добавляет асинхронно выполняемую задачу в бота. Может все к хуям повесить, если использовать
         запрещенные функции.
        """

        class DummyCommand(bot.module_handler.Command):
            name = "dummy"  # имя команды
            desc = "Хуй пизда?"  # описание команды
            args = ""  # необходимые аргументы команды (без имени)

            # метод команды, выполняется, думаю, понтно когда.
            async def run(self, message: discord.Message, args: str, keys: List[str]) -> bool:
                # Универсальная команда для отправления эмбедов с заголовком, авой бота и текстом.
                # Подробнее в kaizen85modules.py
                await bot.send_info_embed(message.channel, bot.module_handler.params["test_param"], "Проверка")
                return True  # True - команда выполнена, False - недостаточно аргументов
                # (в таком случае пользователю отправится помощь о команде
        # bot.module_handler.add_command(DummyCommand(), self)  # добавление команды
