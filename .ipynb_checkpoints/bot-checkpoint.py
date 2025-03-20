from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import pandas as pd
import numpy as np
import numpy.random as npr
##### TO DO: forzare ogni input in uppercase
try:
    dataframe = pd.read_csv('punticarrom.csv')
    colonne = dataframe.columns.tolist()
    giocatori = ', '.join(colonne)
    if dataframe.empty:
        giocatori = 'nessuno'
except pd.errors.EmptyDataError:
    dataframe = pd.DataFrame()
    giocatori = 'nessuno'
#dataset = pd.read_csv('punticarrom.csv') ## dataset punteggi
#dataregine = pd.read_csv('punti_regina.csv') ## dataset regine
welcome = f'Scoreboard ufficiale per il torneo di Carrom mensile dell\'Appa Polle\nIscritti: {giocatori}\nPremi /help se non sai come utilizzarlo\n'
help_msg = "Comandi disponibili:\n/start - Avvia il bot\n/help - Mostra questo messaggio\n/newplayer - Iscrivi un giocatore\n/score - Aggiungi un risultato\n/stats - Statistiche"



TOKEN = "7615452513:AAFrOmQDfqFXi-UqBRktAXtP_5Oh5ukzq1g"
##### WELCOME
async def start(update: Update, context):
    await update.message.reply_text(welcome)
#### HELP COMMAND
async def help_command(update: Update, context):
    await update.message.reply_text(help_msg)
#####ISCRIZIONE
async def newplayer(update: Update, context: CallbackContext):
    try:
        dataset = pd.read_csv('punticarrom.csv')
    except pd.errors.EmptyDataError:
        dataset = pd.DataFrame()

    try:
        dataregine = pd.read_csv('punti_regina.csv')
    except pd.errors.EmptyDataError:
        dataregine = pd.DataFrame()

    # Controlla se l'utente ha fornito un nome di colonna
    if not context.args:
        await update.message.reply_text("Usa /newplayer <nome_giocatore> per iscriverne uno")
        return

    column_name = str(' '.join(context.args[0:6])).upper()  # Ottiene il nome della colonna dal comando

    if column_name in dataset.columns:
        await update.message.reply_text(f"Il player '{column_name}' esiste già.")
    else:
        dataset[column_name] = None 
        dataregine[column_name] = None # Aggiunge una colonna vuota
        await update.message.reply_text(f"Player '{column_name}' aggiunto!")
        dataset.to_csv('punticarrom.csv', index=False)
        dataregine.to_csv('punti_regina.csv', index=False)
##### PUNTEGGIO
async def score(update:Update, context:CallbackContext):
    if not context.args:
        await update.message.reply_text(' Utilizza il formato <player_che_ha_inserito_la_regina> <punteggio> <altro_player> <punteggio>' )
        return
    dataset = pd.read_csv('punticarrom.csv')
    dataregine = pd.read_csv('punti_regina.csv')
    player_queen = str(context.args[0]).upper()
    score_queen = int(context.args[1])
    player2 = str(context.args[2]).upper()
    score2 = int(context.args[3])
    if score_queen > score2:
        winner = player_queen
    elif score_queen == score2:
        winner = 'entrambi'
    else:
        winner = player2

    if player_queen in dataset.columns and player2 in dataset.columns:
        nuova_riga_punti = {player_queen:score_queen,player2:score2 }
        nuova_riga_regina = {player_queen:1}
        dataset.loc[len(dataset)] = {col: nuova_riga_punti.get(col, np.nan) for col in dataset.columns}
        dataregine.loc[len(dataset)] = {col: nuova_riga_regina.get(col, np.nan) for col in dataregine.columns}
        dataset.to_csv('punticarrom.csv', index=False)
        dataregine.to_csv('punti_regina.csv', index=False)
        await update.message.reply_text(f"Inserito, complimenti a {winner}!!")
        
    if player_queen not in dataset.columns or player2 not in dataset.columns:
        await update.message.reply_text('Controlla che entrambi i players siano iscritti')
        
async def stats(update: Update, context: CallbackContext):
    dataset = pd.read_csv('punticarrom.csv')
    dataregine = pd.read_csv('punti_regina.csv')
    if not context.args:
        await update.message.reply_text(f'/stats <player> per stat individuali.\nRiassunto:\n{dataset.mean().to_string()}')
        

    column = str(context.args[0]).upper()

    if column not in dataset.columns:
        await update.message.reply_text(f"{column} non è iscritto. Players iscritti : {', '.join(dataset.columns)}")
        return

    mean_value = dataset[column].mean()
    std_value = dataset[column].std()
    n_games = dataset[column].count()
    await update.message.reply_text(f"Stats di {column}:\nPunteggio medio: {mean_value:.2f}\nDeviazione standard: {std_value:.2f}\n# partite: {n_games}")



app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))  # Registering the /help command
app.add_handler(CommandHandler("newplayer", newplayer))  # Registra il comando /addcolumn
app.add_handler(CommandHandler('score',score)) # registra comando punteggio
app.add_handler(CommandHandler('stats',stats)) #registra comando stats

if __name__ == "__main__":
    app.run_polling()
