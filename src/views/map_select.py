import discord
import os
from enum import Enum

from models.player import Player
from utils.json_manager import maps_json

class MapSelect_View(discord.ui.View):
    class MapSelectionState(Enum):
        GAMEMODE = 1
        MAP = 2
        CONFIRM = 3

    def __init__(self, message: discord.InteractionMessage, player1: Player, player2: Player):
        super().__init__(timeout=None)
        self.message = message
        self.player1 = player1
        self.player2 = player2

        self.selected_gamemode = ""
        self.selected_map = ""       
        self.map_id = -1                
        self.img_name = ""              
        self.img_path = ""              
        self.state = self.MapSelectionState.GAMEMODE
        self.is_ended = False
        
        self.gamemode_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[GAME MODE]\n═════════════════════════════",
            description="Please choose a game mode :"
        )
        self.map_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[MAP]\n═════════════════════════════",
            description="Please choose a map :"
        )
        self.confirm_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[CONFIRM]\n═════════════════════════════",
            description=f"Do you choose {self.selected_map} ?"
        )
    
    async def update_confirm_embed(self):
        self.confirm_embed.description = f"Do you choose {self.selected_map} ?"

    async def update_view(self):
        self.clear_items()

        if self.state == self.MapSelectionState.GAMEMODE:
            self.add_item(self.Gamemode_Select(self))
            await self.message.edit(content=f"{self.player1.user.mention} vs {self.player2.user.mention}", embed=self.gamemode_embed, view=self, attachments=[])
        elif self.state == self.MapSelectionState.MAP:
            self.add_item(self.Map_Select(self))
            self.add_item(self.Return_Button(self))
            await self.message.edit(content=f"{self.player1.user.mention} vs {self.player2.user.mention}", embed=self.map_embed, view=self, attachments=[])
        elif self.state == self.MapSelectionState.CONFIRM:
            await self.update_confirm_embed()
            
            self.img_path = maps_json[self.selected_gamemode]["maps"][self.map_id]["path"]
            self.img_name = os.path.basename(self.img_path)
            attachments = [discord.File(self.img_path, filename=self.img_name)]
            self.confirm_embed.set_image(url=f"attachment://{self.img_name}")

            self.add_item(self.Accept_Button(self))
            self.add_item(self.Decline_button(self))
            await self.message.edit(content=f"{self.player1.user.mention} vs {self.player2.user.mention}", embed=self.confirm_embed, view=self, attachments=attachments)


    class Gamemode_Select(discord.ui.Select):
        def __init__(self, parent:'MapSelect_View'):
            self.parent = parent
            options=[
                discord.SelectOption(label="Gem Grab", emoji=maps_json["Gem Grab"]["emoji"]),
                discord.SelectOption(label="Heist", emoji=maps_json["Heist"]["emoji"]),
                discord.SelectOption(label="Bounty", emoji=maps_json["Bounty"]["emoji"]),
                discord.SelectOption(label="Brawl Ball", emoji=maps_json["Brawl Ball"]["emoji"]),
                discord.SelectOption(label="Hot Zone", emoji=maps_json["Hot Zone"]["emoji"]),
                discord.SelectOption(label="Knockout", emoji=maps_json["Knockout"]["emoji"])
            ]
            super().__init__(placeholder="Game Modes", options=options)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id == self.parent.player1.user.id:
                await interaction.response.defer()
                self.parent.selected_gamemode = self.values[0]
                self.parent.state = self.parent.MapSelectionState.MAP
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {self.parent.player1.user.nick} can interact with this dropdown menu !", ephemeral=True)

        
    class Map_Select(discord.ui.Select):
        def __init__(self, parent:'MapSelect_View'):
            self.parent = parent
            options=[
                discord.SelectOption(label=maps_json[self.parent.selected_gamemode]["maps"][0]["name"], emoji=maps_json[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=maps_json[self.parent.selected_gamemode]["maps"][1]["name"], emoji=maps_json[self.parent.selected_gamemode]["emoji"]),
                discord.SelectOption(label=maps_json[self.parent.selected_gamemode]["maps"][2]["name"], emoji=maps_json[self.parent.selected_gamemode]["emoji"])
            ]
            super().__init__(placeholder=maps_json[self.parent.selected_gamemode]["placeholder"], options=options)
        
        def return_id_map(self):
            for id in range(3):
                if self.values[0] == maps_json[self.parent.selected_gamemode]["maps"][id]["name"]:
                    return id
            else:
                return -1

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id == self.parent.player1.user.id:
                await interaction.response.defer()
                self.parent.selected_map = self.values[0]
                self.parent.map_id = self.return_id_map()
                self.parent.state = self.parent.MapSelectionState.CONFIRM
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {self.parent.player1.user.nick} can interact with this dropdown menu !", ephemeral=True)
        

    class Return_Button(discord.ui.Button):
        def __init__(self, parent:'MapSelect_View'):
            self.parent = parent
            super().__init__(label="Return", style=discord.ButtonStyle.gray)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id == self.parent.player1.user.id:
                await interaction.response.defer()
                self.parent.state = self.parent.MapSelectionState.GAMEMODE
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {self.parent.player1.user.nick} can click on this button !", ephemeral=True)


    class Accept_Button(discord.ui.Button):
        def __init__(self, parent:'MapSelect_View'):
            self.parent = parent 
            super().__init__(label="Accept Map", style=discord.ButtonStyle.blurple)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id == self.parent.player1.user.id:
                await interaction.response.defer()
                self.parent.is_ended = True
                self.parent.stop()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {self.parent.player1.user.nick} can click on this button !", ephemeral=True)


    class Decline_button(discord.ui.Button):
        def __init__(self, parent:'MapSelect_View'):
            self.parent = parent
            super().__init__(label="Decline Map", style=discord.ButtonStyle.danger)

        async def callback(self, interaction: discord.Interaction):
            if(interaction.user.id == self.parent.player1.user.id):
                await interaction.response.defer()
                self.parent.state = self.parent.MapSelectionState.GAMEMODE
                await self.parent.update_view()
            else:
                await interaction.response.defer(ephemeral=True)
                await interaction.followup.send(f"Only {self.parent.player1.user.nick} can click on this button !", ephemeral=True)