from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import pycountry
import google.generativeai as genai
from datetime import datetime
import os
import config

genai.configure(api_key=os.getenv('GENAI'))

model = genai.GenerativeModel('gemini-pro')

TOKEN: Final = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME: Final = "@ballerionBot"

API_KEY: Final = os.getenv('WEATHER_API')
BASE_URL: Final = "https://api.openweathermap.org/data/2.5/weather?"

NEWS_API_KEY: Final = os.getenv('NEWS_API')
menstruation = {
  "menstrual_cycle": [
    {
      "day": 1,
      "symptoms": {
        "Physical Symptoms": ["Cramping", "Bloating", "Fatigue", "Headaches", "Lower Back Pain", "Abdominal Pain"],
        "Emotional Symptoms": ["Mood Swings", "Irritability", "Crying Spells"]
      },
      "description": "Menstruation has just begun, and hormone levels are low. Physical symptoms are most intense."
    },
    {
      "day": 2,
      "symptoms": {
        "Physical Symptoms": ["Cramping", "Bloating", "Fatigue", "Headaches", "Lower Back Pain"],
        "Emotional Symptoms": ["Mood Swings", "Irritability"]
      },
      "description": "Menstruation continues, and physical symptoms start to subside."
    },
    {
      "day": 3,
      "symptoms": {
        "Physical Symptoms": ["Bloating", "Fatigue", "Headaches"],
        "Emotional Symptoms": ["Mood Swings", "Anxiety"]
      },
      "description": "Menstruation is still ongoing, and physical symptoms are decreasing."
    },
    {
      "day": 4,
      "symptoms": {
        "Physical Symptoms": ["Bloating", "Fatigue"],
        "Emotional Symptoms": ["Mood Swings", "Irritability"]
      },
      "description": "Menstruation is ending, and physical symptoms are minimal."
    },
    {
      "day": 5,
      "symptoms": {
        "Physical Symptoms": ["Breast Tenderness", "Digestive Changes"],
        "Emotional Symptoms": ["Mood Swings", "Anxiety"]
      },
      "description": "Menstruation has ended, and the body is preparing for ovulation. Hormone levels are increasing."
    },
    {
      "day": 6,
      "symptoms": {
        "Physical Symptoms": ["Breast Tenderness", "Digestive Changes", "Acne"],
        "Emotional Symptoms": ["Mood Swings", "Anxiety", "Depression"]
      },
      "description": "The body is preparing for ovulation, and hormone levels are increasing. Physical symptoms are mild, but emotional symptoms may persist."
    },
    {
      "day": 7,
      "symptoms": {
        "Physical Symptoms": ["Increased Cervical Mucus", "Bloating"],
        "Emotional Symptoms": ["Increased Confidence", "Increased Energy"]
      },
      "description": "The body is preparing for ovulation, and hormone levels are increasing. Physical symptoms are becoming more noticeable."
    },
    {
      "day": 8,
      "symptoms": {
        "Physical Symptoms": ["Increased Cervical Mucus", "Mild Pelvic Pain", "Light Spotting"],
        "Emotional Symptoms": ["Improved Mood", "Increased Creativity"]
      },
      "description": "Ovulation is approaching, and physical symptoms are becoming more intense."
    },
    {
      "day": 9,
      "symptoms": {
        "Physical Symptoms": ["Increased Cervical Mucus", "Mild Pelvic Pain", "Light Spotting", "Breast Tenderness"],
        "Emotional Symptoms": ["Increased Confidence", "Increased Energy", "Improved Mood"]
      },
      "description": "Ovulation is likely to occur today, and physical symptoms are at their peak."
    },
    {
      "day": 10,
      "symptoms": {
        "Physical Symptoms": ["Increased Cervical Mucus", "Mild Pelvic Pain", "Light Spotting", "Breast Tenderness"],
        "Emotional Symptoms": ["Improved Mood", "Increased Creativity"]
      },
      "description": "Ovulation has likely occurred, and physical symptoms are starting to subside."
    },
    {
      "day": 11,
      "symptoms": {
        "Physical Symptoms": ["Increased Cervical Mucus", "Bloating"],
        "Emotional Symptoms": ["Increased Confidence", "Increased Energy"]
      },
      "description": "The body is preparing for the luteal phase, and hormone levels are decreasing."
    },
    {
      "day": 12,
      "symptoms": {
        "Physical Symptoms": ["Bloating", "Increased Urination"],
        "Emotional Symptoms": ["Improved Mood", "Increased Sensitivity"]
      },
      "description": "The luteal phase has begun, and physical symptoms are becoming more noticeable."
    },
    {
        "day": 13,
        "symptoms": {
            "Physical Symptoms": ["Increased Energy", "Mild Breast Tenderness", "Light Bloating"],
            "Emotional Symptoms": ["Improved Mood", "Increased Confidence", "Mild Irritability"]
        },
        "description": "Hormone levels are rising, and ovulation is approaching. Physical symptoms are mild, and emotional symptoms are generally positive."
    },
    {
        "day": 14,
        "symptoms": {
            "Physical Symptoms": ["Increased Cervical Mucus", "Breast Tenderness", "Mild Bloating"],
            "Emotional Symptoms": ["Improved Mood", "Increased Libido", "Mild Mood Swings"]
        },
        "description": "Ovulation is approaching, and hormone levels are increasing. Physical symptoms are mild, and emotional symptoms are generally positive."
    },
    {
        "day": 15,
        "symptoms": {
            "Physical Symptoms": ["Peak Cervical Mucus", "Breast Tenderness", "Mild Cramping"],
            "Emotional Symptoms": ["Increased Libido", "Improved Mood", "Mild Anxiety"]
        },
        "description": "Ovulation is likely to occur today or tomorrow, and hormone levels are at their peak. Physical symptoms are more pronounced, and emotional symptoms are intense."
    },
    {
        "day": 16,
        "symptoms": {
            "Physical Symptoms": ["Ovulation Pain", "Increased Cervical Mucus", "Breast Tenderness"],
            "Emotional Symptoms": ["Increased Libido", "Improved Mood", "Mild Irritability"]
        },
        "description": "Ovulation has likely occurred, and hormone levels are still high. Physical symptoms are intense, and emotional symptoms are strong."
    },
    {
        "day": 17,
        "symptoms": {
            "Physical Symptoms": ["Decreased Cervical Mucus", "Mild Breast Tenderness", "Fatigue"],
            "Emotional Symptoms": ["Mood Swings", "Mild Anxiety", "Decreased Libido"]
        },
        "description": "Hormone levels are starting to drop, and physical symptoms are subsiding. Emotional symptoms are becoming more unpredictable."
    },
    {
        "day": 18,
        "symptoms": {
            "Physical Symptoms": ["Fatigue", "Mild Bloating", "Digestive Changes"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more pronounced. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 19,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 20,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 21,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming terrible. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 22,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 23,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 24,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable."
    },
    {
        "day": 25,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Heavier Flow Preparation"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Anticipation of Menstruation"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable. The body is preparing for menstruation."
    },
    {
        "day": 26,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Heavier Flow Preparation", "Spotting or Light Bleeding"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Anticipation of Menstruation", "Relief"]
        },
        "description": "Hormone levels have dropped to very low levels. Emotional symptoms are intense and unpredictable. The body is preparing for menstruation, and spotting or light bleeding may occur."
    },
    {
        "day": 27,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Heavier Flow Preparation", "Spotting or Light Bleeding", "Menstrual Cramps"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Anticipation of Menstruation", "Relief", "Acceptance"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable. The body is preparing for menstruation, and spotting or light bleeding may occur. Menstrual cramps may start."
    },
    {
        "day": 28,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Heavier Flow Preparation", "Spotting or Light Bleeding", "Menstrual Cramps"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Anticipation of Menstruation", "Relief", "Acceptance"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable. The body is preparing for menstruation, and spotting or light bleeding may occur. Menstrual cramps may start."
    },
    {
        "day": 29,
        "symptoms": {
            "Physical Symptoms": ["Increased Fatigue", "Breast Tenderness", "Mild Cramping", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Heavier Flow Preparation", "Spotting or Light Bleeding", "Menstrual Cramps"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Anticipation of Menstruation", "Relief", "Acceptance"]
        },
        "description": "Hormone levels continue to drop, and physical symptoms are becoming more intense. Emotional symptoms are intense and unpredictable. The body is preparing for menstruation, and spotting or light bleeding may occur. Menstrual cramps may start."
    },
    {
        "day": 30,
        "symptoms": {
            "Physical Symptoms": ["Menstrual Cramps", "Heavy Bleeding", "Bloating", "Digestive Changes", "Mild Headaches", "Food Cravings", "Mild Back Pain", "Fatigue", "Breast Tenderness"],
            "Emotional Symptoms": ["Mood Swings", "Irritability", "Anxiety", "Sadness", "Restlessness", "Emotional Sensitivity", "Frustration", "Impatience", "Overwhelm", "Relief", "Acceptance"]
        },
        "description": "Menstruation has begun. Physical symptoms are intense, with heavy bleeding, menstrual cramps, and fatigue. Emotional symptoms are still intense, but relief and acceptance are starting to set in."
    }
  ]
}

def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def days_between_sysdate(d1):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    sysdate = datetime.now()
    return abs((sysdate - d1).days)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am a Game of Thrones bot, straight from Westeros. I am here to burn all your queries with my bot fire. With my entire small council, I am ready to assist you. And for a fact, I am experienced in high Valyrian too. 🌸')

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. Where would you like me to send my White Walkers? 🌸")
    context.user_data["weather_step"] = "city"

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. This is Lord Gemini Varys, the infamous Modern-Spider. 🌸")
    context.user_data["search_step"] = "prompt"

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Valar dohaeris. Where would you like me to send a raven? 🌸")
    context.user_data["news_step"] = "country"

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.chucknorris.io/jokes/random"
    response = requests.get(url)
    data = response.json()
    joke = data['value']
    await update.message.reply_text(joke)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    github_url = "https://github.com/ananyab1909/Stella-Bot" 
    portfolio_url = "https://dub.sh/ananyabiswas" 
    bot_info = "This is a multi purpose bot developed in python.\n" \
                "It has integrated api services and embedded women healthcare\n" \
               "It's maintained by Ananya Biswas and is open-source.\n" \
               "Feel free to contribute or report issues on GitHub!"

    keyboard = [
        [InlineKeyboardButton("GitHub Repository", url=github_url)],
        [InlineKeyboardButton("Creator Portfolio", url=portfolio_url)],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(bot_info, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rytsas. Skorkydoso glaesā? Valar dohaeris 🌸.\n/start - greets with a welcome message\n/weather - quick weather forecast of any city\n/search - investigate any topic within a snap\n/news - latest news headlines of any country\n/joke - adds a twirl of Chuck Norris humour\n/health - tracks your menstrual cycle and ovulation, along with symptoms")

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [{"text": "User Details", "callback_data": "user_details"}],
        [{"text": "Track Your Cycle", "callback_data": "track_cycle"}]
    ]
    reply_markup = {"inline_keyboard": keyboard}
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    context.user_data["health_step"] = "option"

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

    if "health_step" in context.user_data:
        if context.user_data["health_step"] == "name":
            user_name = update.message.text.strip()
            if "user_names" not in context.bot_data:
                context.bot_data["user_names"] = []
            context.bot_data["user_names"].append(user_name)
            user_name = update.message.text.strip()
            context.user_data["name"] = user_name
            await update.message.reply_text("Now, tell me about your menstrual cycle. When did it start (yyyy-mm-dd)")
            context.user_data["health_step"] = "start_date"
            return

        if context.user_data["health_step"] == "start_date":
            start_date_input = update.message.text.strip()
            context.user_data["start_date"] = start_date_input
            if "start_date" not in context.bot_data:
                context.bot_data["start_date"] = []
            context.bot_data["start_date"].append(start_date_input)
            await update.message.reply_text("Is your menstruation cycle ongoing or ended? (Enter 'ongoing' or 'ended')")
            context.user_data["health_step"] = "status"
            return

        if context.user_data["health_step"] == "status":
            status = update.message.text.strip().lower()
            context.user_data["status"] = status

            if status == "ended":
                await update.message.reply_text("When did your last menstrual cycle end? (yyyy-mm-dd)")
                context.user_data["health_step"] = "end_date"
                status = "ended"
                if "start_date" not in context.bot_data:
                    context.bot_data["start_date"] = []
                context.bot_data["start_date"].append(status)
                return

            elif status == "ongoing":
                cycle_length = days_between_sysdate(context.user_data["start_date"]) + 1
                estimated_cycle_length = 28
                context.user_data["cycle_duration"] = estimated_cycle_length
                current_day = cycle_length
                status = "ongoing"
                if "start_date" not in context.bot_data:
                    context.bot_data["start_date"] = []
                context.bot_data["start_date"].append(status)

                for day in menstruation["menstrual_cycle"]:
                    if day["day"] == current_day:
                        response_text = f"Day {day['day']}:\n"
                        response_text += "Physical Symptoms:\n"
                        for symptom in day["symptoms"]["Physical Symptoms"]:
                            response_text += f"- {symptom}\n"
                        response_text += "Emotional Symptoms:\n"
                        for symptom in day["symptoms"]["Emotional Symptoms"]:
                            response_text += f"- {symptom}\n"
                        response_text += day["description"]
                        await update.message.reply_text(response_text)

                del context.user_data["health_step"]
                return
            else:
                await update.message.reply_text("Invalid input. Please enter 'ongoing' or 'ended'.")
                return

        if context.user_data["health_step"] == "end_date":
            end_date_input = update.message.text.strip()
            context.user_data["end_date"] = end_date_input
            start = context.user_data["start_date"]
            end = context.user_data["end_date"]
            estimated_cycle_length = days_between(start, end)
            context.user_data["cycle_duration"] = estimated_cycle_length
            
            cycle_length = estimated_cycle_length
            current_day = days_between_sysdate(start) + 1

            for day in menstruation["menstrual_cycle"]:
                if day["day"] == current_day:
                    response_text = f"Day {day['day']}:\n"
                    response_text += "Physical Symptoms:\n"
                    for symptom in day["symptoms"]["Physical Symptoms"]:
                        response_text += f"- {symptom}\n"
                    response_text += "Emotional Symptoms:\n"
                    for symptom in day["symptoms"]["Emotional Symptoms"]:
                        response_text += f"- {symptom}\n"
                    response_text += day["description"]
                    await update.message.reply_text(response_text)

            del context.user_data["health_step"]
            return

    if "search_step" in context.user_data:
        if context.user_data["search_step"] == "prompt":
            prompt = text.strip()
            response = model.generate_content(["You will generate answers within 75 tokens. Write in a continuous flow, avoiding bulleted lists." + prompt])
            await update.message.reply_text(response.text)
            del context.user_data["search_step"] 
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
            
            await update.message.reply_text("Valar dohaeris. Hail, seven Kingdoms. My raven is here. Command where to poke his nose. 🌸", reply_markup=reply_markup)
            context.user_data["country_code"] = country_code
            context.user_data["news_step"] = "category"

        return

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    option = query.data

    if option in ["business", "entertainment", "general", "health", "science", "sports", "technology"]:
        country_code = context.user_data["country_code"]
        url = f"https://newsapi.org/v2/top-headlines?country={country_code}&category={option}&lang=en&apiKey={NEWS_API_KEY}"
        try:
            response = requests.get(url).json()
            articles = response['articles']
            news_message = "My Master of Whispers report that \n"
            for article in articles[:5]:
                news_message += f"{article['title']}\n{article['url']}\n\n"
            await query.message.reply_text(news_message)
        except requests.exceptions.RequestException as e:
            await query.message.reply_text(f"Error: {e}")
            
    elif option == "user_details":
        if "user_names" in context.bot_data and "start_date" in context.bot_data:
            user_names = context.bot_data["user_names"]
            start_dates = context.bot_data["start_date"]
            user_details_message = "User Details:\n"
            for i, (name, start_date) in enumerate(zip(user_names, start_dates)):
                user_details_message += f"{i+1}. {name}  Cycle started on : {start_date}\n"
            await query.message.reply_text(user_details_message)
        else:
            await query.message.reply_text("No user details available.")
            
    elif option == "track_cycle":
        await query.message.reply_text("Dracarys for your pain! Tell me your name. 🌸")
        context.user_data["health_step"] = "name"


print("Starting bot ...")
app = Application.builder().token(TOKEN).build()


app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('weather', weather_command))
app.add_handler(CommandHandler('search', search_command))
app.add_handler(CommandHandler('news', news_command))
app.add_handler(CommandHandler('health', health_command))
app.add_handler(CommandHandler('joke', joke_command))
app.add_handler(CommandHandler('help', help_command))
app.add_handler(CommandHandler('info', info_command))
app.add_handler(CallbackQueryHandler(button_callback))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Starting Polling ...")
app.run_polling()
