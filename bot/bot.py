import disnake
from disnake.ext import commands
import requests
import json

bot = commands.InteractionBot()


@bot.slash_command(name="get_user", description="По имени пользователя получает всю информацию о нём")
async def get_user(inter: disnake.ApplicationCommandInteraction, user: str):
    url = f"https://zhabki.ru/api/v1/getuser"
    response = requests.get(url, params={"username": user})
    if response.status_code == 200:
        data = response.json()
        await inter.response.send_message(f'Пользователь: {data["account"]["name"]}/@{data["account"]["username"]}\n'
                                          f'ID: {data["account"]["id"]}\n'
                                          f'Описание профиля: {data["account"]["bio"]}\n'
                                          f'ID подписчиков: {data["account"]["followers"]}', ephemeral=True)
    else:
        await inter.response.send_message("Ошибка на стороне сервера", ephemeral=True)


@bot.event
async def on_ready():
    print("Бот готов!")


bot.run("MTIzMDUyNjY3OTM0MDgxNDMzNg.GjMxgc.Jlx4M5GOoSXIeY_7T-pQDWjKKJKBYgHYUoTbkg")
