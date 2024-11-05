import discord
import asyncio
from enum import Enum
from typing import List, Optional

from models.player import Player
from utils.json_manager import brawlers_json
from views.map_select import MapSelect_View

class BanPhase_View(discord.ui.View):
    class BanSelectionState(Enum):
        RARITY = 1
        BRAWLERS = 2
        CONFIRM = 3
    
    
    def __init__(self, message: discord.InteractionMessage, player1: Player, player2: Player, map_view: MapSelect_View):
        super().__init__(timeout=None)  # A modifier ?
        self.message = message
        self.player1 = player1
        self.player2 = player2
        self.map_view = map_view
        
        self.first_pick = Player.get_first_player(player1=player1, player2=player2)
        self.last_pick = Player.get_last_player(player1=player1, player2=player2)

        self.timestamp = 0
        self.emote_tbd = "<:tbd:1272563663835889757>"
        self.buttons = [
            discord.ui.Button(custom_id="P1", style=discord.ButtonStyle.gray), 
            discord.ui.Button(custom_id="P2", style=discord.ButtonStyle.gray)
        ]
        self.update_button_labels()
        self.add_item(self.buttons[0])
        self.add_item(self.buttons[1])
        self.followup: List[discord.InteractionMessage] = [None,None]                   # Need typing List
        self.instance_view: List[Optional['BanPhase_View.Player_View']] = [None, None]  # Need typing Optional ==> Indique que la liste peut etre None ou PlayerView  
        self.selected_rarity = ["", ""] 
        self.selected_brawler = [-1, -1]
        self.banned_brawler = [
            [{"Rarity": "", "Id_Brawler": -1},{"Rarity": "", "Id_Brawler": -1},{"Rarity": "", "Id_Brawler": -1}],
            [{"Rarity": "", "Id_Brawler": -1},{"Rarity": "", "Id_Brawler": -1},{"Rarity": "", "Id_Brawler": -1}]
        ]
        self.remaining_bans = [3,3]
        self.state = [self.BanSelectionState.RARITY, self.BanSelectionState.RARITY]
        self.is_ended = [False, False]

        self.instance_embed = discord.Embed(
            title="⚠️DO NOT DISMISS THIS MESSAGE OR RESTART DISCORD⚠️",
            description=f"Your Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}\nPlease choose a rarity :"
        )

    def update_button_labels(self):
        self.buttons[0].label = f"Click here {self.first_pick.user.nick} !"
        self.buttons[1].label = f"Click here {self.last_pick.user.nick} !"

        self.buttons[0].callback = self.p1_button_callback
        self.buttons[1].callback = self.p2_button_callback

    async def p1_button_callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.first_pick.user.id:
            await interaction.response.defer(ephemeral=True)
            self.followup[0] = await interaction.followup.send(embed=self.instance_embed, ephemeral=True, wait=True)
            self.instance_view[0] = self.Player_View(self, 0, self.followup[0])
            await self.followup[0].edit(view=self.instance_view[0])
            await self.instance_view[0].update_view()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {self.player1.user.nick} can click on this button !", ephemeral=True)

    async def p2_button_callback(self, interaction: discord.Interaction):
        if  interaction.user.id == self.last_pick.user.id:
            await interaction.response.defer(ephemeral=True)
            self.followup[1] = await interaction.followup.send(embed=self.instance_embed, ephemeral=True, wait=True)
            self.instance_view[1] = self.Player_View(self, 1, self.followup[1])
            await self.followup[1].edit(view=self.instance_view[1])
            await self.instance_view[1].update_view()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {self.player2.user.nick} can click on this button !", ephemeral=True)
    
    async def timer(self):
        self.clear_items()
        self.timestamp = 10

        rarity_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[BAN PHASE]\n═════════════════════════════\n{self.first_pick.user.nick}'s turn in {self.timestamp:02}seconds\n═════════════════════════════",
            description=f"{self.first_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}\n{self.last_pick.user.nick}'s Bans : {self.emote_tbd} {self.emote_tbd} {self.emote_tbd}"
        )
        attachments = [discord.File(self.map_view.img_path, filename=self.map_view.img_name)]
        rarity_embed.set_thumbnail(url=f"attachment://{self.map_view.img_name}")

        await self.message.edit(embed=rarity_embed, attachments=attachments)

        for seconds in range(self.timestamp, -1, -1):
            rarity_embed.title = f"═════════════════════════════\n[DRAFT SIMULATION]\n[BAN PHASE]\n═════════════════════════════\n{self.first_pick.user.nick}'s turn in {seconds:02} seconds\n═════════════════════════════"

            await self.message.edit(embed=rarity_embed)
            await asyncio.sleep(1)
            if self.is_ended[0] and self.is_ended[1]:
                self.stop()
                break
        
        if not self.is_ended[0] or not self.is_ended[1]:
            self.stop()

    class Player_View(discord.ui.View):
        def __init__(self, parent: 'BanPhase_View', id_player, followup: discord.InteractionMessage):
            super().__init__(timeout=None)
            self.id_player = id_player
            self.parent = parent
            self.message = followup
            self.brawler_view: 'BanPhase_View.Brawler_View'

            self.rarity_embed = discord.Embed(
                title="⚠️DO NOT DISMISS THIS MESSAGE OR RESTART DISCORD⚠️",
            )

            self.brawler_embed = discord.Embed(
                title="⚠️DO NOT DISMISS THIS MESSAGE OR RESTART DISCORD⚠️",
            )

            self.confirm_embed = discord.Embed(
                title="⚠️DO NOT DISMISS THIS MESSAGE OR RESTART DISCORD⚠️",
            )
        

        async def update_embed(self):
            match(self.parent.remaining_bans[self.id_player]):
                case 3:
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.RARITY:
                        self.rarity_embed.description=f"Your Bans : {self.parent.emote_tbd} {self.parent.emote_tbd} {self.parent.emote_tbd}\nPlease choose a rarity :"
                    
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.BRAWLERS:
                        self.brawler_embed.description=f"Your Bans : {self.parent.emote_tbd} {self.parent.emote_tbd} {self.parent.emote_tbd}\nPlease choose a brawler :"
                    
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.CONFIRM:
                        self.confirm_embed.description=(
                        f"Your Bans : {self.parent.emote_tbd} {self.parent.emote_tbd} {self.parent.emote_tbd}\nDo you want to ban : "
                        f"{brawlers_json[self.parent.selected_rarity[self.id_player]][self.parent.selected_brawler[self.id_player]]["portrait"]} ?"
                        )
                case 2:
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.RARITY:
                        self.rarity_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} "
                        f"{self.parent.emote_tbd} {self.parent.emote_tbd}\nPlease choose a rarity :"
                        )
                    
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.BRAWLERS:
                        self.brawler_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} "
                        f"{self.parent.emote_tbd} {self.parent.emote_tbd}\nPlease choose a brawler :"
                        )
                    
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.CONFIRM:
                        self.confirm_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} " 
                        f"{self.parent.emote_tbd} {self.parent.emote_tbd}\nDo you want to ban : "
                        f"{brawlers_json[self.parent.selected_rarity[self.id_player]][self.parent.selected_brawler[self.id_player]]["portrait"]} ?"
                        )
                case 1:
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.RARITY:
                        self.rarity_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} "
                        f"{brawlers_json[self.parent.banned_brawler[self.id_player][1]["Rarity"]][self.parent.banned_brawler[self.id_player][1]["Id_Brawler"]]["portrait"]} "
                        f"{self.parent.emote_tbd}\nPlease choose a rarity :"
                        )
                
                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.BRAWLERS:
                        self.brawler_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} " 
                        f"{brawlers_json[self.parent.banned_brawler[self.id_player][1]["Rarity"]][self.parent.banned_brawler[self.id_player][1]["Id_Brawler"]]["portrait"]} "
                        f"{self.parent.emote_tbd}\nPlease choose a brawler :"
                        )

                    if self.parent.state[self.id_player] == self.parent.BanSelectionState.CONFIRM:
                        self.confirm_embed.description=(
                        f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} " 
                        f"{brawlers_json[self.parent.banned_brawler[self.id_player][1]["Rarity"]][self.parent.banned_brawler[self.id_player][1]["Id_Brawler"]]["portrait"]} "
                        f"{self.parent.emote_tbd}\nDo you want to ban : " 
                        f"{brawlers_json[self.parent.selected_rarity[self.id_player]][self.parent.selected_brawler[self.id_player]]["portrait"]} ?"
                        )

        async def update_view(self):
            self.clear_items()
            await self.update_embed()

            if self.parent.state[self.id_player] == self.parent.BanSelectionState.RARITY:
                self.add_item(self.parent.Rarity_Select(self.parent, self.id_player))
                await self.message.edit(embed=self.rarity_embed, view=self)
            elif self.parent.state[self.id_player] == self.parent.BanSelectionState.BRAWLERS:
                self.brawler_view = self.parent.Brawler_View(self.parent, self.id_player)
                await self.message.edit(embed=self.brawler_embed, view=self.brawler_view)
            elif self.parent.state[self.id_player] == self.parent.BanSelectionState.CONFIRM:
                self.add_item(self.parent.Accept_Button(self.parent, self.id_player))
                self.add_item(self.parent.Decline_Button(self.parent, self.id_player))
                await self.message.edit(embed=self.confirm_embed, view=self)


    
    class Rarity_Select(discord.ui.Select):
        def __init__(self, parent: 'BanPhase_View', id_player):
            self.parent = parent
            self.id_player = id_player
            options=[
                discord.SelectOption(label="Starting & Rare", emoji="<:icon_catalogue_skins_rare:1273679610583715851>"),
                discord.SelectOption(label="Super Rare", emoji="<:icon_catalogue_skins_super_rare:1273679618733506631>"),
                discord.SelectOption(label="Epic", emoji="<:icon_catalogue_skins_epic:1273679627860054127>"),
                discord.SelectOption(label="Mythic", emoji="<:icon_catalogue_skins_mythic:1273679638211596369>"),
                discord.SelectOption(label="Legendary", emoji="<:icon_catalogue_skins_legendary:1273679645409284189>")
            ]
            super().__init__(placeholder="Rarity", options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.parent.selected_rarity[self.id_player] = self.values[0]
            self.parent.state[self.id_player] = self.parent.BanSelectionState.BRAWLERS
            await self.parent.instance_view[self.id_player].update_view()


    class Brawler_View(discord.ui.View):
        def __init__(self, parent: 'BanPhase_View', id_player):
            super().__init__(timeout=None)
            self.parent = parent
            self.id_player = id_player
            self.total_buttons = self.button_amount()
            self.buttons: List['discord.ui.Button'] = []
            self.next_page = False
            self.add_buttons()

        def button_amount(self):
            match self.parent.selected_rarity[self.id_player]:
                case "Starting & Rare":
                    return 9
                case "Super Rare":
                    return 10
                case "Epic":
                    return 13
                case "Mythic":
                    return 13
                case "Legendary":
                    return 11
        
        def add_buttons(self):
            self.clear_items()

            if self.next_page:
                self.index = self.total_buttons
                self.total_buttons += self.total_buttons
            else:
                self.index = 0
                self.total_buttons = self.button_amount()
            
            self.buttons.clear()
            for id_brawler in range(self.index, self.total_buttons):
                button = discord.ui.Button(
                    emoji=brawlers_json[self.parent.selected_rarity[self.id_player]][id_brawler]["pin"], 
                    custom_id=str(id_brawler), 
                    style=discord.ButtonStyle.blurple
                )
    
                async def button_callback(interaction: discord.Interaction, button=button):
                    await self.handle_button_click(interaction, button)
    
                button.callback = button_callback
                self.buttons.append(button)
                

            for index in range(self.button_amount()):
                self.add_item(self.buttons[index])
            
            self.add_item(self.parent.Return_Button(self.parent, self.id_player))
            
            if self.total_buttons >= 13:
                self.add_item(self.parent.Paginator_Button(self.parent, self.id_player))
        
        async def handle_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer(ephemeral=True)
            self.parent.selected_brawler[self.id_player] = int(button.custom_id)
            self.parent.state[self.id_player] = self.parent.BanSelectionState.CONFIRM
            await self.parent.instance_view[self.id_player].update_view()


    class Return_Button(discord.ui.Button):
        def __init__(self, parent: 'BanPhase_View', id_player):
            self.parent = parent
            self.id_player = id_player
            super().__init__(label="Return", style=discord.ButtonStyle.gray)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.parent.state[self.id_player] = self.parent.BanSelectionState.RARITY
            await self.parent.instance_view[self.id_player].update_view()


    class Paginator_Button(discord.ui.Button):
        def __init__(self, parent: 'BanPhase_View', id_player):
            self.parent = parent
            self.id_player = id_player
            super().__init__(label="⏪⏩", style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            if not self.parent.instance_view[self.id_player].brawler_view.next_page:
                self.parent.instance_view[self.id_player].brawler_view.next_page = True
            else:
                self.parent.instance_view[self.id_player].brawler_view.next_page = False

            self.parent.instance_view[self.id_player].brawler_view.clear_items()
            self.parent.instance_view[self.id_player].brawler_view.add_buttons()
            await self.parent.instance_view[self.id_player].message.edit(view=self.parent.instance_view[self.id_player].brawler_view)


    class Accept_Button(discord.ui.Button):
        def __init__(self, parent: 'BanPhase_View', id_player):
            self.parent = parent
            self.id_player = id_player
            super().__init__(label="Accept", style=discord.ButtonStyle.blurple)
        
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)

            self.index_brawler = (3 - self.parent.remaining_bans[self.id_player]) % 3
            self.parent.banned_brawler[self.id_player][self.index_brawler]["Rarity"] = self.parent.selected_rarity[self.id_player]
            self.parent.banned_brawler[self.id_player][self.index_brawler]["Id_Brawler"] = self.parent.selected_brawler[self.id_player]
            self.parent.remaining_bans[self.id_player] -= 1

            if self.parent.remaining_bans[self.id_player] > 0:
                self.parent.state[self.id_player] = self.parent.BanSelectionState.RARITY
                await self.parent.instance_view[self.id_player].update_view()
            else:
                self.parent.is_ended[self.id_player] = True
                self.ended_embed = discord.Embed(
                    title="YOU CAN NOW DISMISS THIS MESSAGE",
                    description=f"Your Bans : {brawlers_json[self.parent.banned_brawler[self.id_player][0]["Rarity"]][self.parent.banned_brawler[self.id_player][0]["Id_Brawler"]]["portrait"]} {brawlers_json[self.parent.banned_brawler[self.id_player][1]["Rarity"]][self.parent.banned_brawler[self.id_player][1]["Id_Brawler"]]["portrait"]} {brawlers_json[self.parent.banned_brawler[self.id_player][2]["Rarity"]][self.parent.banned_brawler[self.id_player][2]["Id_Brawler"]]["portrait"]}"
                )
                await self.parent.instance_view[self.id_player].message.edit(embed=self.ended_embed, view=None)
                self.parent.instance_view[self.id_player].stop()


    class Decline_Button(discord.ui.Button):
        def __init__(self, parent: 'BanPhase_View', id_player):
            self.parent = parent
            self.id_player = id_player
            super().__init__(label="Decline", style=discord.ButtonStyle.danger)
        
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            self.parent.state[self.id_player] = self.parent.BanSelectionState.RARITY
            await self.parent.instance_view[self.id_player].update_view()