import disnake
from disnake.ext import commands
import requests
from dotenv import load_dotenv
import os

bot = commands.InteractionBot()
load_dotenv()
server_api_key = os.getenv('API_KEY')


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
async def del_post(inter: disnake.ApplicationCommandInteraction, postid: int):
    url = f"https://zhabki.ru/api/v1/delpost"
    response = requests.get(url, params={"postid": postid, "key": server_api_key})
    if response.status_code == 200:
        data = response.text
        await inter.response.send_message(data, ephemeral=True)
    else:
        await inter.response.send_message("Ошибка на стороне сервера", ephemeral=True)


@bot.slash_command(name="del_comment", description="Удаляется комментарий по id")
async def del_comment(inter: disnake.ApplicationCommandInteraction, commentid: int):
    url = f"https://zhabki.ru/api/v1/delcomment"
    response = requests.get(url, params={"commentid": commentid, "key": server_api_key})
    if response.status_code == 200:
        data = response.text
        await inter.response.send_message(data, ephemeral=True)
    else:
        await inter.response.send_message("Ошибка на стороне сервера", ephemeral=True)


@bot.slash_command(name="shadow_ban_user", description="Ограничивает функционал пользователю")
async def del_comment(inter: disnake.ApplicationCommandInteraction, user_id: id):
    url = f"https://zhabki.ru/api/v1/banuser"
    response = requests.get(url, params={"userid": user_id, "key": server_api_key})
    if response.status_code == 200:
        data = response.text
        await inter.response.send_message(data, ephemeral=True)
    else:
        await inter.response.send_message("Ошибка на стороне сервера", ephemeral=True)


@bot.event
async def on_ready():
    print("Бот готов!")


bot.run(os.getenv('TOKEN'))
