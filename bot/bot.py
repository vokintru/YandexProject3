import disnake
from disnake.ext import commands
import requests
from dotenv import load_dotenv
import os

bot = commands.InteractionBot()
load_dotenv()


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


@bot.slash_command(name="del_post", description="Удаляется пост по id")
async def get_user(inter: disnake.ApplicationCommandInteraction, postid: int):
    url = f"http://127.0.0.1:5000/api/v1/delpost"
    response = requests.get(url, params={"postid": postid, "key": "boloto_p07G5n1W2E4f8Zq1Xc6T7yU"})
    if response.status_code == 200:
        data = response.text
        print(data)
        await inter.response.send_message(data, ephemeral=True)
    else:
        await inter.response.send_message("Ошибка на стороне сервера", ephemeral=True)


@bot.event
async def on_ready():
    print("Бот готов!")


bot.run(os.getenv('TOKEN'))
