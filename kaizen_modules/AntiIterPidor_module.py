from typing import List
import discord
import kaizen85modules

class Module(kaizen85modules.ModuleHandler.Module):
    name = "AntiIter-Pidor"
    desc = "Автоматический мут за «Итер пидор» и «Пидоррр»"

    async def on_message(self, message, bot):
        if "итер пидор" in message.content.lower() or "пидоррр" in message.content.lower():
            user = message.author

            role = None

            for r in message.guild.roles:
                if r.name == "Muted":
                    role = r

            await message.author.add_roles(role)
			
            await message.add_reaction("🔈")


    #COPYRIGHT D0SH1K ©. All Rights not reserved))))))
    #СПАСИТЕ МЕНЯ! Я В АНАЛЬНОМ РАБСТВЕ AFM
    #ИТЕР ПИДОР! СОСЁТ ЧЛЕН ПРИМАЛИ И ЕГО ЕБЁТ В ЖОПУ НОЙРА
    #GOOGLE топ, Яндекс – говно!
    #D0SH1K
    #https://steamcommunity.com/id/govyajiy_doshirak/
    #мне на всё похуй, у меня конфетка есть и я пою-у-у-у-у-у-у-у... Я ПО-О-О-О-О-Ю-Ю-Ю
    #allformine.ru
    #Клве, верни косарь
    #САС
    #ХЫХ
    #СОС
    #https://vk.com/doshikjpg
    #Дерьмач – отстой
    #идите нах
    # мой пароль от всего timoshA38