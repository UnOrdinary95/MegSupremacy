import os
import discord
from discord import app_commands
from commands.start_draft import start_draft


# Définition des intents pour le bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Activer l'intent pour lire le contenu des messages
client_status = "This is a status !"
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
tree.add_command(start_draft)


# Événement qui se déclenche lorsque le bot est prêt et connecté à Discord
@client.event
async def on_ready():
    print(f"{client.user} is running.")  # Affiche un message dans la console avec le nom d'utilisateur du bot
    await client.change_presence(activity=discord.CustomActivity(client_status))
    try:
        print("Synchronization in progress...")
        await tree.sync()
        print("Synchronization complete. Please reload Discord.\n----------------------------------------------------------------------")
    except Exception as e:
        print(e)

# Démarrage du bot avec le token récupéré depuis les variables d'environnement
client.run(os.getenv("TOKEN"))