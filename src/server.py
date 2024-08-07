import os
import json
import discord
from discord import app_commands
import asyncio
import random


# Définition des intents pour le bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Activer l'intent pour lire le contenu des messages

client_status = "This is a status !"
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Chemin relatif vers le fichier JSON
path = os.path.join("data","map.json")

# Charge le fichier JSON
with open(path, "r") as file:
    data = json.load(file)


class startDraft_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.coin_flip_phase = None
        self.add_item(gamemode_Select()) # à supprimer
        self.add_item(map_Select()) # à supprimer

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        # Supprime le message si le Joueur 2 clique sur "Reject"
        if (interaction.user.id == PLAYER_2.id):
            await interaction.message.delete()
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You have rejected the invitation. The message has been deleted.", ephemeral=True)

            self.coin_flip_phase = False
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {PLAYER_2.global_name} can answer to this message !", ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, Button: discord.ui.Button):
        if (interaction.user.id == PLAYER_2.id):
            await interaction.response.defer()

            self.coin_flip_phase = True
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {PLAYER_2.global_name} can answer to this message !", ephemeral=True)



class gamemode_Select(discord.ui.Select):
    selected_gamemode = "Hot Zone"   # Permet de stocker le nom du mode sélectionnée
    def __init__(self):
        options=[
            discord.SelectOption(label="Gem Grab", emoji=data["Gem Grab"]["emoji"]),
            discord.SelectOption(label="Heist", emoji=data["Heist"]["emoji"]),
            discord.SelectOption(label="Bounty", emoji=data["Bounty"]["emoji"]),
            discord.SelectOption(label="Brawl Ball", emoji=data["Brawl Ball"]["emoji"]),
            discord.SelectOption(label="Hot Zone", emoji=data["Hot Zone"]["emoji"]),
            discord.SelectOption(label="Knockout", emoji=data["Knockout"]["emoji"])
        ]
        super().__init__(placeholder="Game Modes", options=options)

    async def callback(self, interaction: discord.Interaction):
        gamemode_Select.selected_gamemode = self.values[0]


class map_Select(discord.ui.Select):
    selected_map = "Dueling Beetles"     # Permet de stocker le nom de la map sélectionnée
    def __init__(self):
        options=[
            discord.SelectOption(label=data[gamemode_Select.selected_gamemode]["maps"][0], emoji=data[gamemode_Select.selected_gamemode]["emoji"]),
            discord.SelectOption(label=data[gamemode_Select.selected_gamemode]["maps"][1], emoji=data[gamemode_Select.selected_gamemode]["emoji"]),
            discord.SelectOption(label=data[gamemode_Select.selected_gamemode]["maps"][2], emoji=data[gamemode_Select.selected_gamemode]["emoji"])
        ]
        super().__init__(placeholder=data[gamemode_Select.selected_gamemode]["placeholder"], options=options)

    async def callback(self, interaction: discord.Interaction):
        map_Select.selected_map = self.values[0]        


# Événement qui se déclenche lorsque le bot est prêt et connecté à Discord
@client.event
async def on_ready():
    print(f"{client.user} is running.")  # Affiche un message dans la console avec le nom d'utilisateur du bot
    await client.change_presence(activity=discord.CustomActivity(client_status))
    try:
        print("\nSynchronization in progress...")
        await tree.sync()
        print("Synchronization complete. Please reload Discord.")
    except Exception as e:
        print(e)
    

async def cf_phase(message: discord.Message):
    begin_embed = discord.Embed(
        description="The draft is about to start, please wait..."
    )
    await message.edit(content=f"{PLAYER_1.mention} vs {PLAYER_2.mention}", embed=begin_embed, view=None)

    global coin_flip 
    coin_flip = random.randint(0, 1)

    if(coin_flip == 0):
        cf_phase_embed = discord.Embed(
            description=f"🔵{PLAYER_1.mention} has the first pick.\n🔴{PLAYER_2.mention} has the last pick."
        )
    else:
        cf_phase_embed = discord.Embed(
            description=f"🔵{PLAYER_2.mention} has the first pick.\n🔴{PLAYER_1.mention} has the last pick."
        )

    await asyncio.sleep(4)
    await message.edit(content=f"{PLAYER_1.mention} vs {PLAYER_2.mention}", embed=cf_phase_embed)
    await asyncio.sleep(4)

                      
@tree.command(name="start_draft", description="This is a description...")
async def start_draft(interaction: discord.Interaction, user: discord.Member):
    global PLAYER_1, PLAYER_2
    PLAYER_1 = interaction.user
    PLAYER_2 = user

    start_embed = discord.Embed(
        title="Invitation",
        description=f"{interaction.user.mention} wants to practice his drafting skills with you !"
    )
    view = startDraft_View()

    await interaction.response.send_message(content=user.mention, embed=start_embed, view=view)
    message = await interaction.original_response()

    # Attendre que le bouton soit cliqué ou que le timeout soit atteint
    timeout = await view.wait()
    if(timeout):
        await message.edit(content="The invitation has timed out. ", view=None)

    if(view.coin_flip_phase == True):
        print("CF PHASE")
        await cf_phase(message)
    elif(view.coin_flip_phase == False):
        print("Draft rejected.")
    else:
        print("Something unexpected happened")


# Démarrage du bot avec le token récupéré depuis les variables d'environnement
client.run(os.getenv("TOKEN"))

# Test commit