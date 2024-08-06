import os
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

# Permet de sauvegarder le gamemode et la map choisi dans une variable global
save_gamemode = None
save_map = None


class startDraft_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.coin_flip_phase = None
        self.add_item(gamemode_Select()) # à supprimer

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
    def __init__(self):
        options=[
            discord.SelectOption(label="Gem Grab", emoji="<:gem_grab_icon:1269380099975811145>"),
            discord.SelectOption(label="Heist", emoji="<:heist_icon:1269380132674601074>"),
            discord.SelectOption(label="Bounty", emoji="<:bounty_icon:1269380154162155550>"),
            discord.SelectOption(label="Brawl Ball", emoji="<:brawl_ball_icon:1269380142753382531>"),
            discord.SelectOption(label="Hot Zone", emoji="<:hot_zone_icon:1269380163380973598>"),
            discord.SelectOption(label="Knockout", emoji="<:knock_out_icon:1269380175494254662>"),
        ]
        super().__init__(placeholder="Game Modes", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_gamemode
        save_gamemode = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Hard Rock Mine", emoji="<:gem_grab_icon:1269380099975811145>"),
            discord.SelectOption(label="Double Swoosh", emoji="<:gem_grab_icon:1269380099975811145>"),
            discord.SelectOption(label="Undermine", emoji="<:gem_grab_icon:1269380099975811145>"),
        ]
        super.__init__(placeholder="Gem Grab Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]


class mapheist_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Kaboom Canyon", emoji="<:heist_icon:1269380132674601074>"),
            discord.SelectOption(label="Hot Potato", emoji="<:heist_icon:1269380132674601074>"),
            discord.SelectOption(label="Safe Zone", emoji="<:heist_icon:1269380132674601074>"),
        ]

        super.__init__(placeholder="Heist Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
        ]

        super.__init__(placeholder="Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
        ]

        super.__init__(placeholder="Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
        ]

        super.__init__(placeholder="Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
            discord.SelectOption(label="", emoji=""),
        ]

        super.__init__(placeholder="Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        global save_map
        save_map = self.values[0]



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
