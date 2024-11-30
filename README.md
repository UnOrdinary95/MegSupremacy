
# Meg's Supremacy

## Welcome
Welcome to Meg's Supremacy, a personal project developed between July and August 2024.

## Description
This project is a discord bot implemented in Python and utilizes the discord.py library.

## Project Overview

Meg's Supremacy is a discord bot that simulates the drafting experience (Pick & Bans) of Brawl Stars (a mobile game) and determines the winner through a community poll. Created for the pleasure of coding.

## How Pick & Bans works

In order to add another layer of strategy in a competitive game, some developpers adds a new gamemode using the concept of Pick & Bans.

This concept is simple :

#### Character Selection :

- The game provides a wide range of characters to choose from and each with its own weakness (e.g., Character A counter Character B).

#### Unique Character Selection :

- You cannot pick the same character twice.

#### Team Play : 

- You play against your opponents as a team and must ban several characters (there is a limit) so that nobody can pick them.

#### Coin Flip Mechanism : 

- A coin flip is conducted to decide which team initiates the pick phase.This randomization ensures fairness and prevents one team from consistently gaining an advantage by picking first.

#### Banning Phase : 

- While the banning phase is over, each teams can see which characters have been banned from the draft.

#### Character Selection Phase

- After the banning phase, each team selects their characters, excluding the banned ones. This process (Pick Phase) is turn-based.

#### Game start

- Once the Character selection is complete, the game begins.

## Meg's Supremacy Alternative

Instead of the traditional game start, Meg's Supremacy will determines the winner through a community poll.

## Strategic Depth

The strategy is to outsmart your opponent by choosing the right characters to pick for your players, and banning the right ones for your opponent. 

This adds a layer of complexity and tactical depth to the game, making it more engaging and competitive.


## Screenshots

![App Screenshot](https://i.ibb.co/ZTJ4H7F/image.png)

![App Screenshot](https://i.ibb.co/QQQMqKF/image1.png)

![App Screenshot](https://i.ibb.co/mtxJ516/image3.png)

![App Screenshot](https://i.ibb.co/QjqWxjW/image4.png)

## Installation
(Before proceeding, please create your discord bot on the [Discord Developper Portal](https://discord.com/developers/applications), setup a venv and a .env file)

⚠️ Be careful with your token. 

To compile and run this project, follow these steps :
1. Clone the repository using `git clone` or Download ZIP.
2. Activate the virtual environnement.
2. Navigate to the project directory using `cd MegSupremacy/src`.
3. Compile the project using :

```
py server.py 
```

## Status Update

I've been busy with school and haven't played Brawl Stars in a while, but I’ll definitely finish my project someday.

The banning phase is soon completed, it need some fixes (We can pick the same character,...)

- Invitation : ✅
- Coin Flip : ✅
- Banning Phase : ❓
- Picking Phase : ❓
- Community Poll : ❓
