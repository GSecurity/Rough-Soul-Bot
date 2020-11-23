"""This module is used to easily create embed messages and embed message's field(s) in conjunction with Discord.py"""

import discord


# Create discord.Embed fields and returns them
async def create_embed_fields(*fields):
    embed_fields = []
    for field in fields:
        embed_fields.append({'name': field[0], 'value': field[1], 'inline': field[2]})
    return embed_fields


# Create an discord.Embed message and returns it
async def create_embed(title, description, color, author_name, author_icon_url, thumbnail, footer, fields=None):

    embed_message = discord.Embed(
        title=title,
        description=description,
        color=color,
    )
    embed_message.set_author(name=author_name, icon_url=author_icon_url)
    embed_message.set_thumbnail(url=thumbnail)
    if fields is not None:
        for field in fields:
            embed_message.add_field(name=field['name'], value=field['value'], inline=field['inline'])

    embed_message.set_footer(text=footer)

    return embed_message
