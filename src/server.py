import os
import json
import discord
from discord import app_commands
import asyncio
import random
from enum import Enum

PLAYER_1 = None
PLAYER_2 = None

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

# Message initial
message: discord.InteractionMessage


class startDraft_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.coin_flip_phase = None

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        global message, PLAYER_1, PLAYER_2
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
        global message, PLAYER_1, PLAYER_2
        if (interaction.user.id == PLAYER_2.id):
            await interaction.response.defer()

            self.coin_flip_phase = True
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {PLAYER_2.global_name} can answer to this message !", ephemeral=True)


class chooseMap_View(discord.ui.View):
    class mapSelectionState(Enum):
        GAMEMODE = 1
        MAP = 2
        CONFIRM = 3

    def __init__(self):
        super().__init__(timeout=None)
        self.selected_gamemode = None   # Permet de stocker le nom du mode sélectionnée
        self.selected_map = None        # Permet de stocker le nom de la map sélectionnée
        self.state = self.mapSelectionState.GAMEMODE


        self.gamemode_embed = discord.Embed(
            description="Please choose a game mode :"
        )
        self.map_embed = discord.Embed(
            description="Please choose a map :"
        )
        self.confirm_embed = discord.Embed(
            description=f"Do you choose {self.selected_map} ?"
        )
        
    async def update_view(self):
        global message
        self.clear_items()
        if(self.state == self.mapSelectionState.GAMEMODE):
            self.add_item(self.gamemode_Select(self))
            await message.edit(content=f"{PLAYER_1.mention} vs {PLAYER_2.mention}", embed=self.gamemode_embed, view=self)
        elif(self.state == self.mapSelectionState.MAP):
            self.add_item(self.map_Select(self))
            self.add_item(self.return_Button(self))
            await message.edit(content=f"{PLAYER_1.mention} vs {PLAYER_2.mention}", embed=self.map_embed, view=self)
        elif(self.state == self.mapSelectionState.CONFIRM):
            self.add_item(self.accept_Button(self))
            self.add_item(self.decline_button(self))
            await message.edit(content=f"{PLAYER_1.mention} vs {PLAYER_2.mention}", embed=self.confirm_embed, view=self)


    class gamemode_Select(discord.ui.Select):
        def __init__(self, parent):
            self.parent = parent
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
            await interaction.response.defer()
            self.parent.selected_gamemode = self.values[0]
            self.parent.state = self.parent.mapSelectionState.MAP
            await self.parent.update_view()

        
    class map_Select(discord.ui.Select):
        def __init__(self, parent):
            self.parent = parent
            print(f"Mode choisi 2 : {self.parent.selected_gamemode}")
            options=[
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][0], emoji=data[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][1], emoji=data[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][2], emoji=data[self.parent.selected_gamemode]["emoji"])
            ]
            super().__init__(placeholder=data[self.parent.selected_gamemode]["placeholder"], options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            self.parent.selected_map = self.values[0]
            self.parent.state = self.parent.mapSelectionState.CONFIRM
            await self.parent.update_view()

    
    class return_Button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Return", style=discord.ButtonStyle.gray)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            self.parent.state = self.parent.mapSelectionState.GAMEMODE
            await self.parent.update_view()


    class accept_Button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent 
            super().__init__(label="Accept Map", style=discord.ButtonStyle.blurple)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            pass


    class decline_button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Decline Map", style=discord.ButtonStyle.danger)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            self.parent.state = self.parent.mapSelectionState.GAMEMODE
            await self.parent.update_view()


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
    #### OBSOLETE
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
    global message, PLAYER_1, PLAYER_2
    PLAYER_1 = interaction.user
    PLAYER_2 = user
    print(f"Joueur 1 : {PLAYER_1}\nJoueur 2 : {PLAYER_2} ")

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
        print("TEST CHOIX DE MAP")
        print(type(chooseMap_View))
        await message.edit(view=None)
        view = chooseMap_View()
        await message.edit(view=view)
        print("//// Test message début :")
        print(message)
        print("Test message fin ////////")
        global test
        test = 18
        print(f"TEST = {test}")
        await view.update_view()
        # await message.edit(content="Test", view=chooseMap_View(message))
    elif(view.coin_flip_phase == False):
        print("Draft rejected.")
    else:
        print("Something unexpected happened")


# Démarrage du bot avec le token récupéré depuis les variables d'environnement
client.run(os.getenv("TOKEN"))