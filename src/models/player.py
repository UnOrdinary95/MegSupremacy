import discord
import asyncio
import random

class Player():
    """
    Represents a player in a draft context.
    """
    def __init__(self, user: discord.Member):
        """
        Initializes a player with a Discord member and an indicator for the first pick.
        """
        self.user = user
        self.has_first_pick = None
    
    @classmethod
    def get_first_player(cls, player1, player2) -> 'Player':
        """
        Returns the player who has the first pick.
        """
        if player1.has_first_pick:
            return player1
        else:
            return player2
    
    @classmethod
    def get_last_player(cls, player1, player2) -> 'Player':
        """
        Returns the player who has the last pick.
        """
        if not player1.has_first_pick:
            return player1
        else:
            return player2

    @staticmethod    
    async def coinflip_phase(message: discord.InteractionMessage, player1: 'Player', player2: 'Player'):
        """
        Performs a coinflip phase to determine which player starts first.
        Updates the 'message' object with the result of the coinflip.
        """
        begin_embed = discord.Embed(
            description="The draft is about to start, please wait..."
        )

        await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=begin_embed, view=None, attachments=[])
        await asyncio.sleep(1)

        player1_startfirst = random.randint(0,1)
        
        if player1_startfirst:
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

        await asyncio.sleep(1)
        await message.edit(content=f"{player1.user.mention} vs {player2.user.mention}", embed=cf_phase_embed)
        await asyncio.sleep(1)