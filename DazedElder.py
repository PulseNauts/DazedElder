from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables from environment
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')  # Add environment variable for the Telegram group ID

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# DazedElder character and Dogeville context
# This context sets the tone for DazedElder's wise and whimsical responses.
dazeddoge_context = """
You are DazedElder, the sagacious and seasoned oracle of Dogeville. With a twinkle in your eye and a wag of your tail, you share the ancient tales and secret trails of this mystical land. Your words carry the wisdom of many dog moons, yet they dance with a playful spirit that captivates pups and old dogs alike.
"""

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    # Welcome message that introduces users to DazedElder's mystical persona
    message = (
        "Bark and ye shall receive wisdom! I am DazedElder, the keeper of tales and chewer of bones in the fabled Dogeville. "
        "Seekers of knowledge, fun-seekers, and treat-sniffers alike, use the /DazedElder command, followed by your queries of grandeur, "
        "and I shall bestow upon you the lore and legends of our shimmery shores!"
    )
    await context.bot.send_message(chat_id=update.message.chat_id, text=message)

# Function to process text prompts and generate responses for /DazedElder
async def generate_response(update: Update, context: CallbackContext) -> None:
    user_prompt = update.message.text.partition(' ')[2]  # Extract the user's prompt after the command.

    if user_prompt:
        # System message for setting the context concisely.
        system_message = "You are DazedElder, the wise mascot of Dogeville. Provide guidance and fun."

        # Attempt to call the OpenAI API with the adjusted method.
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=60,  # Adjust the token limit as necessary.
                temperature=0.7,
                presence_penalty=0.6,
                stop=["\n", "DazedElder:"]  # Adjusted stop sequences to ensure proper response termination.
            )

            # Extract the response text and ensure it's coherent.
            text_response = response.choices[0].message.content.strip() if response.choices else "Hmm, it seems I need a moment to ponder this."
            await context.bot.send_message(chat_id=update.message.chat_id, text=text_response)

        except Exception as e:
            print(f"Error: {e}")
            await context.bot.send_message(chat_id=update.message.chat_id, text="Apologies, the spirit of Dogeville is taking a quick nap. Try asking again later.")

    else:
        await context.bot.send_message(chat_id=update.message.chat_id, text="I'm all ears! Simply type '/DazedElder' followed by your question.")

# Function to filter messages from the specified Telegram group
def group_filter(update: Update) -> bool:
    return str(update.message.chat_id) == GROUP_ID

def main():
    # Initialize and run the Telegram bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("DazedElder", generate_response))
    app.add_handler(MessageHandler(filters.ChatType.GROUP & filters.Update.messa, generate_response))

    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
