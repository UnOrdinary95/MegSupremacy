import discord

from models.player import Player

class StartDraft_View(discord.ui.View):
    """
    A view that manages the start of a draft process with buttons for accepting or rejecting the invitation.
    """
    def __init__(self, message, player1: Player, player2: Player):
        """
        Initializes the StartDraft_View with the message and the two players involved.

        Parameters:
        - message: The message associated with the draft invitation.
        - player1 (Player): The first player in the draft.
        - player2 (Player): The second player in the draft.
        """
        super().__init__(timeout=None)
        self.message = message
        self.player1 = player1
        self.player2 = player2
        self.is_ended = None

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Handles the reject button click.

        If the user who clicked the button is the second player, the message will be deleted,
        and a notification will be sent. Otherwise, an error message will be sent to the user.

        Parameters:
        - interaction (discord.Interaction): The interaction associated with the button click.
        - button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.player2.user.id:
            await interaction.message.delete()
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You have rejected the invitation. The message has been deleted.", ephemeral=True)
        
            self.is_ended = False
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {self.player2.user.nick} can click on this button !", ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Handles the accept button click.

        If the user who clicked the button is the second player, the invitation will be accepted,
        and the view will be marked as ended. Otherwise, an error message will be sent to the user.

        Parameters:
        - interaction (discord.Interaction): The interaction associated with the button click.
        - button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.player2.user.id:
            await interaction.response.defer()
            
            self.is_ended = True
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Only {self.player2.user.nick} can click on this button !", ephemeral=True)