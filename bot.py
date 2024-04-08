#from neon_db import retrieve_stock_data, create_stock_tables
from fmp_api import get_peers_multiples, get_stock_data, get_indicators
from graph_funcs import graph_peers_multiple_by_type, graph_yield, graph_datatable, graph_tech_optimized
from market_report import how_is_acceleration, how_is_curve, how_is_twist, how_commod, how_commod_volatility
from types_of_multiples import leverage_solvency, valuation, cashflow_dividend, profitability_performance, liquidity_efficiency


from flask import Flask, request, abort
import telebot
from telebot import types
import os
from dotenv import load_dotenv
import io
import matplotlib.pyplot as plt
import matplotlib

comebacker = 'You can always: /restart'

# Setting up Flask
app = Flask(__name__)

matplotlib.use('Agg')

load_dotenv()
BOT_TOKEN = os.getenv('Tg_BOT_TOKEN')
WEBHOOK_URL = 'https://tg-test-test-7be248118a5c.herokuapp.com'  # Your Heroku app's URL

bot = telebot.TeleBot(BOT_TOKEN)


# Dictionary to store user's current ticker
user_tickers = {}

# Welcome message handler
@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_tickers[message.from_user.id] = None  # Reset the ticker for the user

    pin_message = comebacker
    msg_to_pin = bot.send_message(message.chat.id, pin_message)
    bot.pin_chat_message(message.chat.id, msg_to_pin.message_id, disable_notification=False)

    bot.reply_to(message, "Welcome! \nPlease use /set_ticker or \n/yields or \n/commodities to begin analysis.")



#############################################

@bot.message_handler(commands=['commodities'])
def market_analysis_handler(message):
    bot.reply_to(message, "Would you like /commodities_graph or /commodities_report")

#@bot.message_handler(commands=['commodities_graph'])
#def market_analysis_handler(message):
#    analyze_yield(message.chat.id)

@bot.message_handler(commands=['commodities_report'])
def market_analysis_handler(message):
    perform_commod_analysis(message.chat.id)



#############################################

@bot.message_handler(commands=['yields'])
def market_analysis_handler(message):
    bot.reply_to(message, "Would you like /yield_graph or /yield_report")

@bot.message_handler(commands=['yield_graph'])
def market_analysis_handler(message):
    analyze_yield(message.chat.id)

@bot.message_handler(commands=['yield_report'])
def market_analysis_handler(message):
    perform_market_analysis(message.chat.id)



#############################################

# Command to manually set or change the ticker
@bot.message_handler(commands=['set_ticker'])
def command_set_ticker(message):
    msg = bot.reply_to(message, "Please provide a ticker. \nExample: 'AAPL' for Apple Inc.")
    bot.register_next_step_handler(msg, handle_ticker_input)

# General text message handler for setting and confirming tickers
def handle_ticker_input(message):
    if not message.text.startswith('/'):  # This ensures we're not interpreting commands as tickers
        user_tickers[message.from_user.id] = message.text.upper().strip()
        bot.reply_to(message, f"Ticker set to {user_tickers[message.from_user.id]}. You can now use analysis commands like /price or /multiples to analyse.")
    else:
        bot.reply_to(message, "It seems you've entered a command. To set a ticker, please directly type the ticker symbol.")


# Multiples' command
@bot.message_handler(commands=['multiples'])
def perform_analysis_price(message):

    # Placeholder for analysis; replace with your actual function calls
    bot.reply_to(message, f"Choose your focus: \n\n /liquidity_efficiency \n\n /profitability_performance \n\n /leverage_solvency \n\n /cashflow_dividend \n\n /valuation")


# Assuming analyze_multiples is defined to take a parameter specifying the type of multiples analysis
# and you have a mapping of command texts to these types or specific functions.

multiples_analysis_types = {
    'liquidity_efficiency': liquidity_efficiency,
    'profitability_performance': profitability_performance,
    'leverage_solvency': leverage_solvency,
    'cashflow_dividend': cashflow_dividend,
    'valuation': valuation,
}

@bot.message_handler(commands=['liquidity_efficiency', 'profitability_performance', 'leverage_solvency', 'cashflow_dividend', 'valuation'])
def perform_analysis_multiples(message):
    user_id = message.from_user.id
    if user_id not in user_tickers or user_tickers[user_id] is None:
        bot.reply_to(message, "Please /set_ticker first.")
        return

    ticker = user_tickers[user_id]
    analysis_type = message.text[1:]  # Remove the leading '/' from the command to match keys in the dictionary

    if analysis_type in multiples_analysis_types:
        # Call the analysis function with the specified analysis type
        # Note: Adjust the following line based on how your analyze_multiples function is implemented
        analyze_multiples(ticker, message.chat.id, multiples_analysis_types[analysis_type])
    else:
        bot.reply_to(message, "Invalid analysis type. Please choose a valid analysis command.")

@bot.message_handler(commands=['price'])
def handle_price(message):
    user_id = message.from_user.id
    if user_id in user_tickers and user_tickers[user_id]:
        bot.reply_to(message,'Choose:\n\n /clean_price \n\n /moving_avg \n\n /st_deviation')
    else:
        bot.reply_to(message, "Please /set_ticker first.")



# Analysis command handlers
@bot.message_handler(commands=['clean_price'])
def handle_price(message):
    user_id = message.from_user.id
    if user_id in user_tickers and user_tickers[user_id]:
        ticker = user_tickers[user_id]
        analyze_price(ticker, message.chat.id)
    else:
        bot.reply_to(message, "Please /set_ticker first.")

# Analysis command handlers
@bot.message_handler(commands=['moving_avg'])
def handle_price(message):
    user_id = message.from_user.id
    if user_id in user_tickers and user_tickers[user_id]:
        ticker = user_tickers[user_id]
        tech_analysis(message.chat.id, ticker, ["ema", "ema", "ema"] , [10,50,200])
    else:
        bot.reply_to(message, "Please /set_ticker first.")

# Analysis command handlers
@bot.message_handler(commands=['st_deviation'])
def handle_price(message):
    user_id = message.from_user.id
    if user_id in user_tickers and user_tickers[user_id]:
        ticker = user_tickers[user_id]
        tech_analysis(message.chat.id, ticker, ["standardDeviation"], [20])
    else:
        bot.reply_to(message, "Please /set_ticker first.")

#############################################

def analyze_price(ticker, chat_id):
    ticker = ticker.strip().upper()
    data_df = get_stock_data(ticker)  # Assuming this function fetches the required data
    
    if data_df is not None and not data_df.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(data_df['date'], data_df['close'], linestyle='-', color='b')  # Assuming 'date' is the DataFrame index
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.title(f'Stock Close Price for {ticker}')

        # Adjust x-axis ticks to show only some dates
        num_dates = 5  # Number of dates to display
        num_points = len(data_df['date'])
        step = num_points // num_dates
        plt.xticks(data_df['date'][::step])
        
        # Convert plot to PNG image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi = 300)
        buffer.seek(0)
        
        # Send the plot
        bot.send_photo(chat_id, photo=buffer)
        plt.close()  # Close the plot to free up memory
        del data_df

    else:
        bot.send_message(chat_id, "Sorry, I couldn't fetch data for that ticker. Please try again.")


def analyze_multiples(ticker, chat_id, m_type):
    ticker = ticker.strip().upper()
    data_df = get_peers_multiples(ticker)  # Assuming this function returns a DataFrame
    data_df = data_df.set_index('index')

    if not data_df.empty:
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        axs = axs.flatten()

        for ax, multiple in zip(axs, m_type):
            graph_peers_multiple_by_type(multiple, ax, data_df)

        plt.subplots_adjust(wspace=0.33, hspace=0.33)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)

        bot.send_photo(chat_id, photo=buffer)
        plt.close()
        del data_df
    else:
        bot.send_message(chat_id, "Sorry, there was a problem with the multiples analysis.")


def analyze_yield(chat_id):
    graph_yield()
    
    # Convert plot to PNG image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi = 300)
    buffer.seek(0)
    
    # Send the plot
    bot.send_photo(chat_id, photo=buffer)
    plt.close()  # Close the plot to free up memory
    del yield_curve



def perform_market_analysis(chat_id):
    # Call each analysis function and gather outputs
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(5, 4))  # Adjust the figure size as needed
    
    # Example DataFrames
    acceleration_df = how_is_acceleration().reset_index()
    twist_df = how_is_twist().reset_index()
    curve_df = how_is_curve().reset_index()

    # Plot DataFrames in a grid layout
    graph_datatable(axes[0], acceleration_df, 'Acceleration Avg(Month)')
    graph_datatable(axes[1], twist_df, 'Major Twists - Thresh: 5%')
    graph_datatable(axes[2], curve_df, 'Latest Dynamic')

    # Adjust layout
    plt.subplots_adjust(hspace=0.5)  # Reduce the vertical space between rows
    
    # Save the plot as a PNG file in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    buffer.seek(0)

    # Send the plot
    bot.send_photo(chat_id, photo=buffer)
    plt.close()  # Close the plot to free up memory


def perform_commod_analysis(chat_id):
    # Call each analysis function and gather outputs
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(5, 4))  # Adjust the figure size as needed
    
    # Example DataFrames
    commod_volume = how_commod('changePercent').reset_index()
    commod_ret = how_commod('volume').reset_index()
    commod_stdev = how_commod_volatility().reset_index()

    # Plot DataFrames in a grid layout
    graph_datatable(axes[0], commod_ret, 'Avg Returns %')
    graph_datatable(axes[1], commod_stdev, 'Avg Volatility')
    graph_datatable(axes[2], commod_volume, "Avg Volume ('000)")

    # Adjust layout
    plt.subplots_adjust(hspace=0.5)  # Reduce the vertical space between rows
    
    # Save the plot as a PNG file in memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0.1, dpi=300)
    buffer.seek(0)

    # Send the plot
    bot.send_photo(chat_id, photo=buffer)
    plt.close()  # Close the plot to free up memory


# Example tech_analysis function
def tech_analysis(chat_id, ticker, indicators, periods):
    ticker = ticker.strip().upper()
    df = get_indicators(ticker, indicators, periods)
    buffer = graph_tech_optimized(df, ticker)
    
    # Here you would replace bot.send_photo with the appropriate method for your bot framework
    bot.send_photo(chat_id, photo=buffer)
    
    buffer.close()  # Optionally close the buffer if you're done with it



@app.route('/', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return abort(403)

# Start the Flask server
if __name__ == '__main__':
    bot.remove_webhook()  # Remove previous webhook if any
    bot.set_webhook(url=WEBHOOK_URL)  # Set new webhook URL
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))  # Start Flask server