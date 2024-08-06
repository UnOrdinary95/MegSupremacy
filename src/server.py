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


class startDraft_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.coin_flip_phase = None
        self.add_item(gamemode_Select()) # à supprimer
        self.add_item(maphotzone_Select())  # à supprimer

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
        self.selected_gamemode = None   # Permet de stocker le nom du mode sélectionnée
        options=[
            discord.SelectOption(label="Gem Grab", emoji="<:gem_grab_icon:1270412969179742319>"),
            discord.SelectOption(label="Heist", emoji="<:heist_icon:1270413044757037086>"),
            discord.SelectOption(label="Bounty", emoji="<:bounty_icon:1270412997663264838>"),
            discord.SelectOption(label="Brawl Ball", emoji="<:brawl_ball_icon:1270412985659293747>"),
            discord.SelectOption(label="Hot Zone", emoji="<:hot_zone_icon:1270413010036457482>"),
            discord.SelectOption(label="Knockout", emoji="<:knock_out_icon:1270413017602855065>"),
        ]
        super().__init__(placeholder="Game Modes", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_gamemode = self.values[0]


class mapgemgrab_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None    # Permet de stocker le nom de la map sélectionnée
        options=[
            discord.SelectOption(label="Hard Rock Mine", emoji="<:gem_grab_icon:1270412969179742319>"),
            discord.SelectOption(label="Double Swoosh", emoji="<:gem_grab_icon:1270412969179742319>"),
            discord.SelectOption(label="Undermine", emoji="<:gem_grab_icon:1270412969179742319>"),
        ]
        super().__init__(placeholder="Gem Grab Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]


class mapheist_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None
        options=[
            discord.SelectOption(label="Kaboom Canyon", emoji="<:heist_icon:1270413044757037086>"),
            discord.SelectOption(label="Hot Potato", emoji="<:heist_icon:1270413044757037086>"),
            discord.SelectOption(label="Safe Zone", emoji="<:heist_icon:1270413044757037086>"),
        ]

        super().__init__(placeholder="Heist Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]


class mapbounty_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None
        options=[
            discord.SelectOption(label="Shooting Star", emoji="<:bounty_icon:1270412997663264838>"),
            discord.SelectOption(label="Canal Grande", emoji="<:bounty_icon:1270412997663264838>"),
            discord.SelectOption(label="Hideout", emoji="<:bounty_icon:1270412997663264838>"),
        ]

        super().__init__(placeholder="Bounty Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]


class mapbrawlball_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None
        options=[
            discord.SelectOption(label="Center Stage", emoji="<:brawl_ball_icon:1270412985659293747>"),
            discord.SelectOption(label="Pinball Dreams", emoji="<:brawl_ball_icon:1270412985659293747>"),
            discord.SelectOption(label="Penalty Kick", emoji="<:brawl_ball_icon:1270412985659293747>"),
        ]

        super().__init__(placeholder="Brawl Ball Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]


class maphotzone_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None
        options=[
            discord.SelectOption(label="Dueling Beetles", emoji="<:hot_zone_icon:1270413010036457482>"),
            discord.SelectOption(label="Open Business", emoji="<:hot_zone_icon:1270413010036457482>"),
            discord.SelectOption(label="Parallel Plays", emoji="<:hot_zone_icon:1270413010036457482>"),
        ]

        super().__init__(placeholder="Hot Zone Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]


class mapknockout_Select(discord.ui.Select):
    def __init__(self):
        self.selected_map = None
        options=[
            discord.SelectOption(label="Belle's Rock", emoji="<:knock_out_icon:1270413017602855065>"),
            discord.SelectOption(label="Out in the Open", emoji="<:knock_out_icon:1270413017602855065>"),
            discord.SelectOption(label="Flaring Phoenix", emoji="<:knock_out_icon:1270413017602855065>"),
        ]

        super().__init__(placeholder="Knockout Maps", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected_map = self.values[0]



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