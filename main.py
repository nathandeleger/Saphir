import discord
import sqlite3
from discord import app_commands
from discord.ext import commands
from config import TOKEN

def init_db():
    connexion = sqlite3.connect('database.db')
    cursor = connexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        points INTEGER DEFAULT 0
        )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discord_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        FOREIGN KEY (discord_id) REFERENCES users(discord_id)
        )
        ''')
    connexion.commit()
    connexion.close()

init_db()
user_tasks = {}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} est prêt.")
    try :
        synced = await bot.tree.sync()
        print(f"Slash commands synchronisés : {len(synced)} commandes.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des slash commands : {e}")

@bot.tree.command()
async def hello(ctx):
    await ctx.send(f"Salut {ctx.author.mention} !")

@bot.tree.command(name="tache", description="Ajoutez une tâche à votre liste de chose à faire")
@app_commands.describe(tache ="la tâche que vous souhaitez ajouter")
async def task(interaction: discord.Interaction,tache: str):
        user_id = interaction.user.id
        connexion = sqlite3.connect('database.db')
        cursor = connexion.cursor()
        cursor.execute('SELECT * FROM tasks WHERE discord_id = ? AND task = ?', (user_id, tache))
        existing_task = cursor.fetchone()
        if existing_task:
             await interaction.response.send_message(f"Vous avez déjà une tâche similaire : '{tache}'.", ephemeral=True)
        else :
             cursor.execute('INSERT INTO tasks (discord_id, task) VALUES(?, ?)', (user_id, tache))
             connexion.commit()
             await interaction.response.send_message(f"Votre tâche '{tache}' à bien été ajoutée à votre liste !", ephemeral=True)
        connexion.close()

@bot.tree.command(name="manage", description="Supprimez une tâche de votre liste")
async def manage(interaction: discord.Interaction, tache :str):
        user_id = interaction.user.id
        connexion = sqlite3.connect('database.db')
        cursor = connexion.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task = ? AND discord_id = ?', (tache, user_id))
        task = cursor.fetchone()
        if task :
            cursor.execute('DELETE FROM tasks WHERE task = ?', (tache,))
            connexion.commit()
            await interaction.response.send_message(f"Tâche '{tache}' supprimée.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Aucune tâche '{tache}'.", ephemeral=True)
        connexion.close()

@bot.tree.command(name="liste", description="liste toute vos tâches chose à faire")
async def liste(interaction: discord.Interaction):
        user_id = interaction.user.id
        connexion = sqlite3.connect('database.db')
        cursor = connexion.cursor()
        cursor.execute('SELECT task FROM tasks WHERE discord_id = ? ', (user_id, ))
        tasks = cursor.fetchall()
        if tasks:
            tasks_list = "\n".join([f"- {task[0]}" for task in tasks])
            await interaction.response.send_message(f"Vos tâches : \n{tasks_list}", ephemeral=True)
        else:
            await interaction.response.send_message("Vous n'avez aucune tâche pour le moment.", ephemeral=True)
        connexion.close()


@bot.tree.command(name ="register" , description="enregistrer un utilisateur dans la base de donnée")
async def register(interaction = discord.Interaction):
    user_id = interaction.user.id
    username = interaction.user.name

    connexion = sqlite3.connect('database.db')
    cursor = connexion.cursor()
    cursor.execute('SELECT * FROM users WHERE discord_id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute('INSERT INTO users (discord_id, name) VALUES (?, ?)', (user_id, username))
        connexion.commit()
        await interaction.response.send_message(f"{username}, tu as été enregistré dans la base de données !")
    else:
        await interaction.response.send_message(f"{username}, tu es déjà enregistré.")
    connexion.close()

@bot.tree.command(name="complete", description="Supprimez une tâche de votre liste")
async def complete(interaction: discord.Interaction, tache :str):
        user_id = interaction.user.id
        connexion = sqlite3.connect('database.db')
        cursor = connexion.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task = ? AND discord_id = ?', (tache, user_id))
        task = cursor.fetchone()
        if task :
            cursor.execute('DELETE FROM tasks WHERE task = ?', (tache,))
            connexion.commit()
            await interaction.response.send_message(f"Vous avez complété '{tache}' Bravo !!!!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Aucune tâche '{tache}' à compléter.", ephemeral=True)
        connexion.close()

bot.run(TOKEN)
