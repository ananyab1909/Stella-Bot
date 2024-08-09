from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import openai
import requests
import pycountry
import random
import google.generativeai as genai

genai.configure(api_key='gemini-api-key')

model = genai.GenerativeModel('gemini-pro')

TOKEN: Final = 'telegram-api-token'
BOT_USERNAME: Final = "@ballerionBot"
API_KEY: Final = 'weather-api-key'
BASE_URL: Final = "https://api.openweathermap.org/data/2.5/weather?"
NEWS_API_KEY: Final = 'news-api-key'

got_responses = [
    "The Iron Throne, of course. What else?",
    "The Night King's army is coming for us all.",
    "Winter is coming, but I'm still trying to stay warm.",
    "I'm preparing for battle, what about you?",
    "The Mother of Dragons has spoken, and I'm listening.",
    "I'm trying to stay alive in the Seven Kingdoms, one day at a time.",
    "The Wall is breached, and I'm not sure what's next.",
    "I'm plotting my revenge against the Lannisters.",
    "The Hound is coming for me, I just know it.",
    "I'm trying to find the perfect cup of wine, just like Tyrion.",
]

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am a Game of Thrones character in a GenZ world')

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. Where would you like me to send my White Walkers?")
    context.user_data["weather_step"] = "city"

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. This is Lord Gemini Varys, the infamous Modern-Spider.")
    context.user_data["search_step"] = "prompt"

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. Where would you like me to send a raven?")
    context.user_data["news_step"] = "country"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User({update.message.chat_id}) in {message_type} : "{text}"')

    if "weather_step" in context.user_data:
        if context.user_data["weather_step"] == "city":
            city_name = update.message.text.strip()
            url = BASE_URL + "appid=" + API_KEY + "&q=" + city_name
            try:
                response = requests.get(url).json()
                temp_kelvin = response['main']['temp']
                temp = temp_kelvin - 273.15
                feels_like_kelvin = response['main']['feels_like']
                feels_like = feels_like_kelvin - 273.15
                forecast_message = f"Weather in {city_name}: "
                forecast_message += f"Temperature: {temp:.2f}°C."
                forecast_message += f" Feels like: {feels_like:.2f}°C. "
                forecast_message += f"Humidity: {response['main']['humidity']}%. "
                forecast_message += f"Weather condition: {response['weather'][0]['description']}. "
                await update.message.reply_text(forecast_message)
            except requests.exceptions.RequestException as e:
                await update.message.reply_text(f"Error: {e}")
            finally:
                del context.user_data["weather_step"]
        return

    if "search_step" in context.user_data:
        if context.user_data["search_step"] == "prompt":
            prompt = text.strip()
            response = model.generate_content(["You will generate answers within 75 tokens. Write in a continuous flow, avoiding bulleted lists." + prompt])
            await update.message.reply_text(response.text)
        return

    if "news_step" in context.user_data:
        if context.user_data["news_step"] == "country":
            country_name = update.message.text.strip()
            country_code = pycountry.countries.get(name=country_name).alpha_2
            categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

            keyboard = [
                [{"text": "Business", "callback_data": "business"}],
                [{"text": "Entertainment", "callback_data": "entertainment"}],
                [{"text": "General", "callback_data": "general"}],
                [{"text": "Health", "callback_data": "health"}],
                [{"text": "Science", "callback_data": "science"}],
                [{"text": "Sports", "callback_data": "sports"}],
                [{"text": "Technology", "callback_data": "technology"}]
            ]
            reply_markup = {"inline_keyboard": keyboard}
            
            await update.message.reply_text("Valar dohaeris. Hail, seven Kingdoms. My raven is here. Command where to poke his nose.", reply_markup=reply_markup)
            context.user_data["country_code"] = country_code
            context.user_data["news_step"] = "category"

        return

    if message_type == "group":
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category = query.data
    country_code = context.user_data["country_code"]
    
    url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={category}&lang=en&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url).json()
        articles = response['articles']
        news_message = "My Master of Whispers report that \n"
        for article in articles[:5]:
            news_message += f"{article['title']}\n{article['url']}\n\n"
        await query.message.reply_text(news_message)
    except requests.exceptions.RequestException as e:
        await query.message.reply_text(f"Error: {e}")

# Response handler
def handle_response(text):
    command = text.lower()

    if 'hello' in command or 'helluu' in command or 'hellllloooo' in command or 'hellllooo' in command:
        return 'Welcome to Westeros! My dragons says hi to you'
    
    elif 'do' in command or 'abilities' in command:
        return 'I can burn all your queries with my bot fire as I am acquainted with my brother Gemini. And on the contrary I can speak some High Valyrian too! DRACARYS'
    
    elif 'help' in command:
        return 'I have my entire small council here for you. Type /search to look up something, /weather to get quick weather updates, /news to be informed of whats happening around us or just harass my grandpa with me!'
    
    elif 'what' in command or 'hey' in command or 'ssup' in command or 'day' in command:
        return random.choice(got_responses)
    
    elif "joke" in command or "laugh" in command or "funny" in command:
        url = "https://api.chucknorris.io/jokes/random"
        response = requests.get(url)
        data = response.json()
        joke = data['value']
        return joke
    
    else:
        return 'I did not understand that'

print("Starting bot ...")
app = Application.builder().token(TOKEN).build()


app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('weather', weather_command))
app.add_handler(CommandHandler('search', search_command))
app.add_handler(CommandHandler('news', news_command))
app.add_handler(CallbackQueryHandler(button_callback))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


print("Starting Polling ...")
app.run_polling()
