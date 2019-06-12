"""
Скрипт для вывода (бес)полезной статистики по сообщениям в каналах серверов.
Может работать медленно, потому что мне лень делать рефакторинг свеженаписанного говна.
"""
import os
import sys

import discord


class UserInfo:
    name = ""
    messages_count = 0

    def __init__(self, name):
        self.name = name


class ChannelInfo:
    name = ""
    messages_count = 0
    everyone_count = 0
    here_count = 0

    popular_words = {}
    user_stats = {}

    def __init__(self, name):
        self.name = name


client = discord.Client()


@client.event
async def on_ready():
    print("Вход выполнен от %s." % client)

    try:
        guild_id = int(input("Введите ID сервера > "))
    except ValueError:
        print("Вы ввели неверное значение.")
        await client.logout()
        return

    if not client.get_guild(guild_id):
        print("Сервер не найден.")
        await client.logout()
        return

    guild: discord.Guild = client.get_guild(guild_id)

    print("Найден сервер \"%s\".\nСбор информации..." % guild.name)

    channel_stats = {}

    for channel in guild.text_channels:
        print("\n\033[93mОбработка канала #%s..." % channel.name)

        if channel.id not in channel_stats:
            channel_stats[channel.id] = ChannelInfo("#" + channel.name)
        channel_info = channel_stats[channel.id]

        async for message in channel.history(limit=None, reverse=True):
            channel_info.messages_count += 1

            if "@everyone" in message.content:
                channel_info.everyone_count += 1
            elif "@here" in message.content:
                channel_info.here_count += 1

            for word in message.clean_content.split():
                if word not in "!@#$%^&*()_+-={}[];'\\:\"|<>?,./":
                    word = word.lower()
                    if word not in channel_info.popular_words:
                        channel_info.popular_words[word] = 1

                    channel_info.popular_words[word] += 1

            if message.author.id not in channel_info.user_stats:
                channel_info.user_stats[message.author.id] = UserInfo(str(message.author))
            user_info = channel_info.user_stats[message.author.id]

            user_info.messages_count += 1

            sys.stdout.write("\r\033[94mОбработано сообщений: %s\033[0m" % channel_info.messages_count)

    guild_messages_count = 0
    guild_everyone_count = 0
    guild_here_count = 0
    guild_popular_words = {}
    guild_user_stats = {}

    for _, channel_info in channel_stats.items():
        guild_messages_count += channel_info.messages_count
        guild_everyone_count += channel_info.everyone_count
        guild_here_count += channel_info.here_count

        for word, count in channel_info.popular_words.items():
            if word not in guild_popular_words:
                guild_popular_words[word] = 0

            guild_popular_words[word] += count

        for user_id, user_info in channel_info.user_stats.items():
            if user_info not in guild_user_stats:
                guild_user_stats[user_id] = 0

            guild_user_stats[user_id] += user_info.messages_count

    guild_popular_words_string = ""
    words = 0
    for key, value in sorted(guild_popular_words.items(), key=lambda item: item[1], reverse=True):
        if words == 10:
            break

        guild_popular_words_string += "%s - %s\n" % (key, value)
        words += 1

    guild_user_stats_string = ""
    users = 0
    for key, value in sorted(guild_user_stats.items(), key=lambda item: item[1], reverse=True):
        if users == 10:
            break

        guild_user_stats_string += "%s - %s сообщений\n" % (
            guild.get_member(key).name if guild.get_member(key) else "Пользователь недоступен", value)
        users += 1

    print("\n\033[92mСбор завершен. Идет запись в файл...")

    with open("%s_guild_stats.txt" % guild_id, "w", encoding="utf-8") as f:
        text = """
=====Статистика сообщений сервера %s========
Всего сообщений: %s
Всего @everyone: %s
Всего @here: %s
Топ 10 популярных слов:
%s
Топ 10 пользователей по сообщениям:
%s
""" % (guild.name, guild_messages_count, guild_everyone_count, guild_here_count, guild_popular_words_string,
       guild_user_stats_string)

        f.write(text)
        f.close()


client.run(os.environ.get("kaizen85_token"))
