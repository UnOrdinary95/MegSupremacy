import os
import discord
from discord import app_commands

from utils.json_manager import brawlers_json
from models.player import Player
from views.start_draft import StartDraft_View
from views.map_select import MapSelect_View
from views.ban_phase import BanPhase_View

# Définition des intents pour le bot Discord
intents = discord.Intents.default()
intents.message_content = True  # Activer l'intent pour lire le contenu des messages

client_status = "This is a status !"
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


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


@tree.command(name="start_draft", description="This is a description...")
async def start_draft(interaction: discord.Interaction, user: discord.Member):
    player1 = Player(user=interaction.user)
    player2 = Player(user=user)

    await interaction.response.send_message(content=f"{user.mention}")
    message = await interaction.original_response()
    
    start_embed = discord.Embed(
        title="Invitation",
        description=f"{interaction.user.mention} wants to practice his drafting skills with you !"
    )
    starting_view = StartDraft_View(message, player1, player2)
    await message.edit(content=f"{user.mention}" , embed=start_embed, view=starting_view)

    # Attendre que le bouton soit cliqué ou que le timeout soit atteint
    timeout = await starting_view.wait()
    if timeout:
        await message.edit(content="The invitation has timed out.", view=None)
    
    # Vue 'start_draft' terminé ?
    if starting_view.is_ended:
        await Player.coinflip_phase(message, player1, player2)
        await message.edit(view=None)
        map_view = MapSelect_View(message, player1, player2)
        await message.edit(view=map_view)
        await map_view.update_view()
    elif not starting_view.is_ended:
        return
    else:
        print("\nSomething unexpected happened.")
        return
    
    # Attendre que le bouton soit cliqué ou que le timeout soit atteint
    timeout = await map_view.wait()
    if(timeout):
        await message.edit(content="The invitation has timed out.", view=None)

    # Vue 'chooseMap' terminé ?
    if map_view.is_ended:
        await message.edit(view=None)
        ban_view = BanPhase_View(message, player1, player2, map_view)
        await message.edit(view=ban_view)
        await ban_view.timer()
    else:
        print("\nSomething unexpected happened.")
        return
    
    # Attendre que la fin de la phase de draft
    timeout = await ban_view.wait()
    if(timeout):
        await message.edit(content="The invitation has timed out.", view=None)
    
    # Vue 'Ban' terminé ?
    if ban_view.is_ended[0] and ban_view.is_ended[1]:
        await message.edit(view=None)
        banned_brawler_embed = discord.Embed(
            title=f"═════════════════════════════\n[DRAFT SIMULATION]\n[BAN PHASE]\n═════════════════════════════",
            description=(
                f"{ban_view.first_pick.user.nick}'s Bans : "
                f"{brawlers_json[ban_view.instance_view[0].parent.banned_brawler[0][0]["Rarity"]][ban_view.instance_view[0].parent.banned_brawler[0][0]["Id_Brawler"]]["portrait"]} "
                f"{brawlers_json[ban_view.instance_view[0].parent.banned_brawler[0][1]["Rarity"]][ban_view.instance_view[0].parent.banned_brawler[0][1]["Id_Brawler"]]["portrait"]} "
                f"{brawlers_json[ban_view.instance_view[0].parent.banned_brawler[0][2]["Rarity"]][ban_view.instance_view[0].parent.banned_brawler[0][2]["Id_Brawler"]]["portrait"]} "
                f"\n{ban_view.last_pick.user.nick}'s Bans : "
                f"{brawlers_json[ban_view.instance_view[1].parent.banned_brawler[1][0]["Rarity"]][ban_view.instance_view[1].parent.banned_brawler[1][0]["Id_Brawler"]]["portrait"]} "
                f"{brawlers_json[ban_view.instance_view[1].parent.banned_brawler[1][1]["Rarity"]][ban_view.instance_view[1].parent.banned_brawler[1][1]["Id_Brawler"]]["portrait"]} "
                f"{brawlers_json[ban_view.instance_view[1].parent.banned_brawler[1][2]["Rarity"]][ban_view.instance_view[1].parent.banned_brawler[1][2]["Id_Brawler"]]["portrait"]}"
            )
        )
        banned_brawler_embed.set_thumbnail(url=f"attachment://{map_view.img_name}")
        await message.edit(embed=banned_brawler_embed, attachments=[discord.File(map_view.img_path, map_view.img_name)], view=None)
    elif not ban_view.is_ended[0] or not ban_view.is_ended[1]:
        
        await message.edit(content=f"{player1.user.mention} & {player2.user.mention}, this session has timed out.", embed=None, attachments=[], view=None)
        return
    else:
        print("\nSomething unexpected happened.")
        return

# Démarrage du bot avec le token récupéré depuis les variables d'environnement
client.run(os.getenv("TOKEN"))
