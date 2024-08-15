import os
import sys
import json
import discord
from discord import app_commands
import asyncio
import random
from enum import Enum
from datetime import datetime, timedelta

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


class Player():
    def __init__(self, user: discord.Member):
        self.user = user
        self.coin_flip = self.perform_coin_flip()
        self.has_first_pick = None
    
    def perform_coin_flip(self):
        # Simule un pile ou face, retourne 0 ou 1
        return random.randint(0, 1)
    
    @classmethod
    def get_first_pick(cls, player1, player2):
        if player1.has_first_pick == True:
            return player1
        else:
            return player2
    
    @classmethod
    def get_last_pick(cls, player1, player2):
        if player1.has_first_pick == False:
            return player1
        else:
            return player2


class StartDraft_View(discord.ui.View):
    global message, player1, player2
    
    def __init__(self):
        super().__init__(timeout=None)
        self.is_ended = None

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, Button: discord.ui.Button):
        print(f"{interaction.user.global_name} clicked on the button.")

        # Supprime le message si le Joueur 2 clique sur "Reject"
        if (interaction.user.id == player2.user.id):
            await interaction.message.delete()
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You have rejected the invitation. The message has been deleted.", ephemeral=True)
            self.is_ended = False
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {player2.user.nick} can click on this button !", ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, Button: discord.ui.Button):
        print(f"{interaction.user.global_name} clicked on the button.")

        if (interaction.user.id == player2.user.id):
            await interaction.response.defer()
            self.is_ended = True
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {player2.user.nick} can click on this button !", ephemeral=True)


class ChooseMap_View(discord.ui.View):
    global message, player1, player2

    class MapSelectionState(Enum):
        GAMEMODE = 1
        MAP = 2
        CONFIRM = 3


    def __init__(self):
        super().__init__(timeout=None)
        self.selected_gamemode = None   # Permet de stocker le nom du mode sélectionnée
        self.selected_map = None        # Permet de stocker le nom de la map sélectionnée
        self.map_id = -1                # Permet de stocker l'id de la map (Permettant de savoir easily quel map correspond à quel path)
        self.img_name = None            # Permet de stocker le nom du png
        self.img_path = None            # Permet de stocker le chemin vers le png 
        self.state = self.MapSelectionState.GAMEMODE
        self.is_ended = False
        
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
        self.clear_items()
        if(self.state == self.MapSelectionState.GAMEMODE):
            print("'choose_map' state : GAMEMODE")

            self.add_item(self.Gamemode_Select(self))
            await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=self.gamemode_embed, view=self, attachments=[])
        elif(self.state == self.MapSelectionState.MAP):
            print("'choose_map' state : MAP")

            self.add_item(self.Map_Select(self))
            self.add_item(self.Return_Button(self))
            await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=self.map_embed, view=self, attachments=[])
        elif(self.state == self.MapSelectionState.CONFIRM):
            print("'choose_map' state : CONFIRM")

            self.confirm_embed = discord.Embed(
            description=f"Do you choose {self.selected_map} ?"
            )
            self.img_path = data[self.selected_gamemode]["maps"][self.map_id]["path"]
            self.img_name = os.path.basename(self.img_path)
            # Assurez-vous que file est dans une liste
            attachments = [discord.File(self.img_path, filename=self.img_name)]

            self.confirm_embed.set_image(url=f"attachment://{self.img_name}")

            self.add_item(self.Accept_Button(self))
            self.add_item(self.Decline_button(self))
            await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=self.confirm_embed, view=self, attachments=attachments)


    class Gamemode_Select(discord.ui.Select):
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
            print(f"{interaction.user.global_name} clicked on the button.")

            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.selected_gamemode = self.values[0]
                print(f"Chosen Gamemode : {self.parent.selected_gamemode}")
                self.parent.state = self.parent.MapSelectionState.MAP
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} can interact with this dropdown menu !", ephemeral=True)

        
    class Map_Select(discord.ui.Select):
        def __init__(self, parent):
            self.parent = parent
            options=[
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][0]["name"], emoji=data[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][1]["name"], emoji=data[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=data[self.parent.selected_gamemode]["maps"][2]["name"], emoji=data[self.parent.selected_gamemode]["emoji"])
            ]
            super().__init__(placeholder=data[self.parent.selected_gamemode]["placeholder"], options=options)
        
        def return_id_map(self):
            for id in range(3):
                if self.values[0] == data[self.parent.selected_gamemode]["maps"][id]["name"]:
                    return id
            else:
                return -1

        async def callback(self, interaction: discord.Interaction):
            print(f"{interaction.user.global_name} clicked on the button.")

            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.selected_map = self.values[0]
                self.parent.map_id = self.return_id_map()

                print(f"Chosen Map : {self.parent.selected_map}")
                print(f"Map ID : {self.parent.map_id}")
                self.parent.state = self.parent.MapSelectionState.CONFIRM
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} can interact with this dropdown menu !", ephemeral=True)
                

    
    class Return_Button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Return", style=discord.ButtonStyle.gray)

        async def callback(self, interaction: discord.Interaction):
            print(f"{interaction.user.global_name} clicked on the button.")

            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.state = self.parent.MapSelectionState.GAMEMODE
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} can click on this button !", ephemeral=True)


    class Accept_Button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent 
            super().__init__(label="Accept Map", style=discord.ButtonStyle.blurple)

        async def callback(self, interaction: discord.Interaction):
            print(f"{interaction.user.global_name} clicked on the button.")

            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.is_ended = True
                self.parent.stop()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} can click on this button !", ephemeral=True)


    class Decline_button(discord.ui.Button):
        def __init__(self, parent):
            self.parent = parent
            super().__init__(label="Decline Map", style=discord.ButtonStyle.danger)

        async def callback(self, interaction: discord.Interaction):
            print(f"{interaction.user.global_name} clicked on the button.")

            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.state = self.parent.MapSelectionState.GAMEMODE
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} can click on this button !", ephemeral=True)

class BanPhase_View(discord.ui.View):
    global message, player1, player2, map_view
    class BanSelectionState(Enum):
        RARITY = 1
        BRAWLERS = 2
        CONFIRM = 3
    
    
    def __init__(self):
        super().__init__(timeout=None)  # A modifier ?
        self.first_pick = Player.get_first_pick(player1=player1, player2=player2)
        self.last_pick = Player.get_last_pick(player1=player1, player2=player2)
        self.timestamp = 0
        self.emote_tbd = "<:tbd:1272563663835889757>"
        self.add_item(discord.ui.button(label=f"Click here {self.first_pick.user.nick} !", custom_id="P1", style=discord.ButtonStyle.grey))
        self.add_item(discord.ui.button(label=f"Click here {self.last_pick.user.nick} !", custom_id="P2", style=discord.ButtonStyle.grey))
        self.message_p1 = None
        self.message_p2 = None
        self.selected_rarity = [None, None] 
        self.selected_brawler = [None, None] 
        self.state = [self.BanSelectionState.RARITY, self.BanSelectionState.RARITY]
        self.is_ended = False
    
    @discord.ui.button(custom_id="P1")
    async def p1_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        print(f"{interaction.user.global_name} clicked on the button.")

        if (interaction.user.id == self.first_pick.user.id):
            await interaction.response.defer(ephemeral=True)
            self.message_p1 = await interaction.followup.send()
        await interaction.response.send_message(f"{self.first_pick} a cliqué sur le bouton!")

    async def timer(self):
        self.clear_items()
        self.timestamp = 60

        rarity_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[BAN PHASE]\n═════════════════════════════\n{self.first_pick.user.nick}'s turn in {self.timestamp:02}seconds\n═════════════════════════════",
            description=f"{self.first_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}\n{self.last_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}"
        )
        attachments = [discord.File(map_view.img_path, filename=map_view.img_name)]
        rarity_embed.set_thumbnail(url=f"attachment://{map_view.img_name}")


        await message.edit(embed=rarity_embed, attachments=attachments)

        for i in range(self.timestamp, -1, -1):
            seconds = i
            rarity_embed = discord.Embed(
                title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[BAN PHASE]\n═════════════════════════════\n{self.first_pick.user.nick}'s turn in {seconds:02} seconds\n═════════════════════════════",
                description=f"{self.first_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}\n{self.last_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}"
            )
            attachments = [discord.File(map_view.img_path, filename=map_view.img_name)]
            rarity_embed.set_thumbnail(url=f"attachment://{map_view.img_name}")

            await message.edit(embed=rarity_embed)
            await asyncio.sleep(1)

    async def update_view(self):
        self.clear_items()
        if(self.state == self.BanSelectionState.RARITY):
            print("'ban_phase' : RARITY")

    
    class Rarity_Select(discord.ui.Select):
        def __init__(self, parent):
            self.parent = parent
            options=[
                discord.SelectOption(label="Starting & Rare", emoji="<:icon_catalogue_skins_rare:1273679610583715851>"),
                discord.SelectOption(label="Super Rare", emoji="<:icon_catalogue_skins_super_rare:1273679618733506631>"),
                discord.SelectOption(label="Epic", emoji="<:icon_catalogue_skins_epic:1273679627860054127>"),
                discord.SelectOption(label="Mythic", emoji="<:icon_catalogue_skins_mythic:1273679638211596369>"),
                discord.SelectOption(label="Legendary", emoji="<:icon_catalogue_skins_legendary:1273679645409284189>")
            ]
            super().__init__(placeholder="Rarity", options=options)

        async def callback(self, interaction: discord.Interaction):
            print(f"{interaction.user.global_name} clicked on the button.")
            
            if(interaction.user.id == player1.user.id):
                await interaction.response.defer()
                self.parent.selected_rarity[0] = self.values[0]
                self.parent.state[0] = self.parent.BanSelectionState.BRAWLERS
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {player1.user.nick} & {player2.user.nick} can interact with this dropdown menu !", ephemeral=True)

        


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


async def cf_phase():
    global message, player1, player2

    begin_embed = discord.Embed(
        description="The draft is about to start, please wait..."
    )

    await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=begin_embed, view=None, attachments=[])

    print(f"Player 1 coin = {player1.coin_flip}")
    print(f"Player 2 coin = {player2.coin_flip}")

    if(player1.coin_flip == 0):
        player1.has_first_pick = True
        player2.has_first_pick = False

        cf_phase_embed = discord.Embed(
            description=f"🔵{player1.user.mention} has the first pick.\n🔴{player2.user.mention} has the last pick."
        )
    else:
        player1.has_first_pick = False
        player2.has_first_pick = True

        cf_phase_embed = discord.Embed(
            description=f"🔵{player2.user.mention} has the first pick.\n🔴{player1.user.mention} has the last pick."
        )

    await asyncio.sleep(0)
    await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=cf_phase_embed)
    await asyncio.sleep(0)


async def set_timer(seconds):
    dt = datetime.now()
    future_time = dt + timedelta(seconds=seconds)
    ts = int(future_time.timestamp())
    return ts

@tree.command(name="start_draft", description="This is a description...")
async def start_draft(interaction: discord.Interaction, user: discord.Member):
    global message, player1, player2
    player1 = Player(user=interaction.user)
    player2 = Player(user=user)


    print("PHASE => 'start_draft'")
    print(f"Player 1 : {player1.user}\nPlayer 2 : {player2.user}")
    
    ts = set_timer(60)

    start_embed = discord.Embed(
        title="Inv",
        description=f"{interaction.user.mention} wants to practice his drafting skills with you !"
    )
    view = StartDraft_View()
    ts = await set_timer(60)
    await interaction.response.send_message(content=f"{user.mention} <t:{ts}:R>" , embed=start_embed, view=view)
    message = await interaction.original_response()

    # Attendre que le bouton soit cliqué ou que le timeout soit atteint
    timeout = await view.wait()
    if(timeout):
        await message.edit(content="The invitation has timed out.", view=None)

    # Vue 'start_draft' terminé ?
    if(view.is_ended == True):
        global map_view
        print("\nPHASE => 'choose_map'")

        await message.edit(view=None)
        map_view = ChooseMap_View()
        await message.edit(view=map_view)
        await map_view.update_view()
    elif(view.is_ended == False):
        sys.exit("\nDraft rejected.")
    else:
        sys.exit("\nSomething unexpected happened.")
    
    # Attendre que le bouton soit cliqué ou que le timeout soit atteint
    timeout = await map_view.wait()
    if(timeout):
        await message.edit(content="The invitation has timed out.", view=None)

    # Vue 'chooseMap' terminé ?
    if(map_view.is_ended == True):
        print("\nPHASE => 'coin_flip'")
        await cf_phase()
    else:
        sys.exit("\nSomething unexpected happened.")
    
    await message.edit(view=None)
    ban_view = BanPhase_View()
    await message.edit(view=ban_view)
    await ban_view.timer()


@tree.command(name="timer", description="Start a countdown timer")
async def timer(interaction: discord.Interaction):
    time = 60
    timer_embed = discord.Embed(
        title="Timer",
        description=f"{time} seconds remaining"
    )
    
    await interaction.response.send_message(embed=timer_embed)
    msg = await interaction.original_response()

    while time > 0:
        await asyncio.sleep(0.5)
        time -= 1
        # Update only if the time has changed
        new_embed = discord.Embed(
            title="Timer",
            description=f"{time} seconds remaining"
        )
        await msg.edit(embed=new_embed)

    # Notify when the timer is done
    done_embed = discord.Embed(
        title="Timer",
        description="Time's up!",
        color=discord.Color.red()
    )
    await msg.edit(embed=done_embed)


@tree.command(name="timer2", description="V2")
async def timer2(interaction: discord.Interaction):
    time = 60
    timer_embed = discord.Embed(
        description=f"00:01:00"
    )
    dt = datetime.now()
    future_time = dt + timedelta(seconds=60)
    ts = int(future_time.timestamp())

    await interaction.response.send_message(embed=timer_embed)
    msg = await interaction.original_response()
    
    for x in range(time, 0, -1):
        seconds = x % 60
        minutes = int(x / 60) % 60
        timer_embed = discord.Embed(
            description=f"**00:{minutes:02}:{seconds:02}**"
        )

        await msg.edit(embed=timer_embed)
        await asyncio.sleep(1)




# Démarrage du bot avec le token récupéré depuis les variables d'environnement
client.run(os.getenv("TOKEN"))