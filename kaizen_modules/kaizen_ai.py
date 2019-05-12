import os
import discord
from textgenrnn import textgenrnn
import kaizen85modules

model_files = {"weights_path": "./kaizen.hdf5", "vocab_path": "./textgenrnn_vocab.json",
               "config_path": "./textgenrnn_config.json"}


class Module(kaizen85modules.ModuleHandler.Module):
    name = "KaizenAI"
    desc = "Пожилой киберсыч нового поколения!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        bot.module_handler.add_param("aiTemp", 0.9)

        ok = True
        for _, v in model_files.items():
            if not os.path.isfile(v):
                ok = False
                break

        if not ok:
            bot.logger.log("[Kaizen_AI] Can't find model files. The command will not load.")

            return

        textgen = textgenrnn(weights_path=model_files["weights_path"], vocab_path=model_files["vocab_path"],
                             config_path=model_files["config_path"])

        class CommandAI(bot.module_handler.Command):
            name = "ai"
            desc = "Пожилой ИИ"
            args = "[prefix]"

            async def run(self, message: discord.Message, args, keys):
                prefix = ""
                if len(args) > 0:
                    if args[0][:7] == "prefix=":
                        prefix = message.content[11:]

                ai_text = "".join(textgen.generate(temperature=bot.module_handler.params["aiTemp"], return_as_list=True,
                                                   prefix=prefix))
                await bot.send_info_embed(message.channel, ai_text, "Киберсыч")

                return True

        bot.module_handler.add_command(CommandAI(), self)
