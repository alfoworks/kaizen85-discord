"""
Данный бот может пересылать сообщения в двустороннем порядке с серверов.
Он слушает сообщения, которые ему приходят. Если сообщение с сервера и сервер есть в разрешенном списке,
то бот, используя вебхук, перешлет сообщения в канал категории сервера на главном сервере, при этом
создавая их, если они отсутствуют.
Бот также может пересылать сообщения, которые приходят ему в ЛС, так же в главный сервер.
"""

import datetime
import os
import time

import discord

# Настройки бота.
LOGGED_GUILDS = [157892343163387904]  # ID серверов, за которыми бот будет следить.
MAIN_GUILD = 547876610032926757  # ID "главного" сервера, куда будут пересылаться сообщения.
LOG_DM = True  # Будут ли личные сообщения пересылаться.

# Различная параша для команд и эмбедов.
ERROR_EMOJI = "❌"
OK_EMOJI = "☑"
ERROR_COLOR = 0xFF4C4C
OK_COLOR = 0x6AAF6A

# Имя игры, указанное ниже, будет отображаться в статусе пользователя. Если None, не будет отображаться.
USER_GAME = "Apex Legends"  # Можно вбить что угодно, однако, если дискорд распознает игру, то будет видно её иконку.

# ======================================================
if not os.path.isdir("./logger_data/"):
    os.mkdir("./logger_data/")

client: discord.Client = discord.Client()
main_guild: discord.Guild = None


@client.event
async def on_ready():
    global main_guild
    main_guild = client.get_guild(MAIN_GUILD)

    if not main_guild:
        print("\033[91mНе удалось найти главный сервер")
        await client.logout()
        return

    print("\033[1;32;0mВход выполнен от имени %s (%s)" % (str(client.user), client.user.id))
    print("\033[1;32;0mГлавный сервер: %s" % main_guild.name)
    print("\033[1;32;0mОтслеживаемые сервера: %s" % ", ".join(
        [client.get_guild(guild_id).name if client.get_guild(guild_id) else "Недоступный сервер" for guild_id in
         LOGGED_GUILDS]))

    if USER_GAME:
        await client.change_presence(
            activity=discord.Game(USER_GAME, start=datetime.datetime.utcfromtimestamp(time.time())),
            status=discord.Status.dnd)


@client.event
async def on_message(message: discord.Message):
    if message.guild is not None and message.guild.id in LOGGED_GUILDS and main_guild:
        category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name=message.guild.name)
        channel: discord.TextChannel = discord.utils.get(main_guild.text_channels, name=message.channel.name)

        files = []

        if not category:
            category = await main_guild.create_category(message.guild.name)

        if not channel:
            channel = await main_guild.create_text_channel(message.channel.name, category=category)

        webhook: discord.Webhook = discord.utils.get(await channel.webhooks(), name=channel.name)

        if not webhook:
            webhook = await channel.create_webhook(name=channel.name)

        for attachment in message.attachments:
            await attachment.save(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "wb"))
            files.append(discord.File(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "rb")))

        await webhook.send(content=message.content, avatar_url=message.author.avatar_url, embeds=message.embeds,
                           files=files, username=message.author.nick or message.author.name)
    elif message.guild is not None and message.guild.id == MAIN_GUILD and message.content.startswith(
            "!") and message.author.id != client.user.id and type(message.author) == discord.Member:
        category: discord.CategoryChannel = message.channel.category

        if not category:
            return

        files = []

        for attachment in message.attachments:
            await attachment.save(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "wb"))
            files.append(discord.File(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "rb")))

        if category.name == "DM":
            try:
                user: discord.User = client.get_user(int(message.channel.name))

                await user.send(content=message.content[1:], files=files)
            except ValueError:
                embed = discord.Embed(title="Ошибка", description="Недопустимое имя канала.",
                                      color=ERROR_COLOR)
                await message.channel.send(embed=embed)
                await message.add_reaction(ERROR_EMOJI)
                return
            except Exception as e:
                embed = discord.Embed(title="Ошибка", description="Произошла ошибка при отправке - %s." % e,
                                      color=ERROR_COLOR)
                await message.channel.send(embed=embed)
                await message.add_reaction(ERROR_EMOJI)
                return

            await message.add_reaction(OK_EMOJI)
            return

        guild: discord.Guild = discord.utils.get(client.guilds, name=category.name)

        if not guild:
            return

        channel: discord.TextChannel = discord.utils.get(guild.channels, name=message.channel.name)

        if not channel:
            await message.add_reaction(ERROR_EMOJI)

            embed = discord.Embed(title="Ошибка", description="Данного канала больше нет на сервере.",
                                  color=ERROR_COLOR)
            await message.channel.send(embed=embed)

            return

        await channel.send(content=message.content[1:], files=files)
        await message.add_reaction(OK_EMOJI)
    elif message.guild is None and LOG_DM:
        category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name="DM")
        channel: discord.TextChannel = discord.utils.get(main_guild.text_channels,
                                                         name=str(message.channel.recipient.id))

        files = []

        if not category:
            category = await main_guild.create_category("DM")

        if not channel:
            channel = await main_guild.create_text_channel(str(message.channel.recipient.id), category=category)
            await channel.edit(topic=message.channel.recipient.name)

        webhook: discord.Webhook = discord.utils.get(await channel.webhooks(), name=channel.name)

        if not webhook:
            webhook = await channel.create_webhook(name=channel.name)

        for attachment in message.attachments:
            await attachment.save(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "wb"))
            files.append(discord.File(open("./logger_data/%s_%s" % (attachment.id, attachment.filename), "rb")))

        await webhook.send(content=message.content, avatar_url=message.author.avatar_url, embeds=message.embeds,
                           files=files, username=message.author.name)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if after.guild is None or after.guild not in LOGGED_GUILDS or before.content == after.content:
        return

    category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name=after.guild.name)
    channel: discord.TextChannel = discord.utils.get(main_guild.text_channels, name=after.channel.name)

    files_before = []
    files_after = []

    if not category:
        category = await main_guild.create_category(after.guild.name)

    if not channel:
        channel = await main_guild.create_text_channel(after.channel.name, category=category)

    webhook: discord.Webhook = discord.utils.get(await channel.webhooks(), name=channel.name)

    if not webhook:
        webhook = await channel.create_webhook(name=channel.name)

    # До изменения

    for attachment in before.attachments:
        await attachment.save(
            open("./logger_data/edit_before_%s_%s" % (attachment.id, attachment.filename), "wb"))
        files_before.append(
            discord.File(open("./logger_data/edit_before_%s_%s" % (attachment.id, attachment.filename), "rb")))

    await webhook.send(content="**Пользователь изменил сообщение!\nБыло:**\n" + before.content,
                       avatar_url=before.author.avatar_url, embeds=before.embeds,
                       files=files_before, username=before.author.nick or before.author.name)

    # После изменения

    for attachment in after.attachments:
        await attachment.save(
            open("./logger_data/edit_after_%s_%s" % (attachment.id, attachment.filename), "wb"))
        files_after.append(
            discord.File(open("./logger_data/edit_after_%s_%s" % (attachment.id, attachment.filename), "rb")))

    await webhook.send(content="**Стало:**\n" + after.content,
                       avatar_url=after.author.avatar_url, embeds=after.embeds,
                       files=files_after, username=after.author.nick or after.author.name)


@client.event
async def on_member_join(member: discord.Member):
    if member.guild.id not in LOGGED_GUILDS:
        return

    category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name=member.guild.name)
    channel: discord.TextChannel = discord.utils.get(main_guild.text_channels, name=str(member.guild.id))

    if not category:
        category = await main_guild.create_category(member.guild.name)

    if not channel:
        channel = await main_guild.create_text_channel(str(member.guild.id), category=category)

    webhook: discord.Webhook = discord.utils.get(await channel.webhooks(), name=channel.name)

    if not webhook:
        webhook = await channel.create_webhook(name=channel.name)

    embed = discord.Embed(title="Информация", description="Пользователь зашел на сервер.", color=OK_COLOR)

    await webhook.send(
        avatar_url=member.avatar_url, embed=embed, username=member.name)


@client.event
async def on_member_remove(member: discord.Member):
    if member.guild.id not in LOGGED_GUILDS:
        return

    category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name=member.guild.name)
    channel: discord.TextChannel = discord.utils.get(main_guild.text_channels, name=str(member.guild.id))

    if not category:
        category = await main_guild.create_category(member.guild.name)

    if not channel:
        channel = await main_guild.create_text_channel(str(member.guild.id), category=category)

    webhook: discord.Webhook = discord.utils.get(await channel.webhooks(), name=channel.name)

    if not webhook:
        webhook = await channel.create_webhook(name=channel.name)

    embed = discord.Embed(title="Информация", description="Пользователь покинул сервер.", color=ERROR_COLOR)

    await webhook.send(
        avatar_url=member.avatar_url, embed=embed, username=member.name)


@client.event
async def on_guild_remove(guild):
    if guild.id not in LOGGED_GUILDS:
        return

    category: discord.CategoryChannel = discord.utils.get(main_guild.categories, name=guild.name)
    channel: discord.TextChannel = discord.utils.get(main_guild.text_channels, name=str(guild.id))

    if not category:
        category = await main_guild.create_category(guild.name)

    if not channel:
        channel = await main_guild.create_text_channel(str(guild.id), category=category)

    embed = discord.Embed(title="Внимание", description="АСС была забанена или кикнута с этого сервера.",
                          color=ERROR_COLOR)

    await channel.send(content="@everyone", embed=embed)


client.run(os.environ.get("afmksb_token"), bot=False)
