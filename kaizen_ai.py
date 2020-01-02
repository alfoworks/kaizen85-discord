import discord
import textgenrnn

import kaizen85modules


class Module(kaizen85modules.ModuleHandler.Module):
    name = "KaizenAI"
    desc = "Пожилой киберсыч нового поколения!"

    async def run(self, bot: kaizen85modules.KaizenBot):
        class AICommand(kaizen85modules.ModuleHandler.Command):
            title = ""
            file_name = ""
            color = 0
            model: textgenrnn.textgenrnn

            model_loaded = True

            name = ""
            desc = "ИИ %s"
            args = "[prefix=<prefix>]"

            def __init__(self, title, file_name, command_name, color):
                self.title = title
                self.file_name = file_name
                self.name = command_name
                self.color = color

                self.desc = self.desc % title

                try:
                    self.model = textgenrnn.textgenrnn(weights_path="%s_weights.hdf5" % file_name,
                                                       vocab_path="%s_vocab.json" % file_name,
                                                       config_path="%s_config.json" % file_name)
                except FileNotFoundError:
                    bot.logger.log("Could not find model files for AI %s. The command will not work." % title,
                                   bot.logger.PrintColors.FAIL)

                    self.model_loaded = False
                else:
                    bot.logger.log("Initialized AI with name %s." % self.title, bot.logger.PrintColors.OKBLUE)

            async def run(self, message: discord.Message, args, keys):
                if not self.model_loaded:
                    await bot.send_error_embed(message.channel, "Модель данного ИИ не загружена.")
                    return True

                prefix = None

                if len(args) > 0 and args[0].startswith("prefix="):
                    prefix = " ".join(args)[7:]

                embed = bot.get_special_embed(self.color, "ИИ %s" % self.title)
                embed.description = \
                    self.model.generate(temperature=bot.module_handler.params["aiTemp"], return_as_list=True,
                                        prefix=prefix)[0]

                await message.channel.send(embed=embed)
                return True

        bot.module_handler.add_param("aiTemp", 0.9)

        models = [AICommand("Kaizen", "kaizen", "kz", 0x64E3E1), AICommand("Icarus", "icarus", "ic", 0xFFD700)]

        for model in models:
            bot.module_handler.add_command(model, self)
