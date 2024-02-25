from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import openai
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Record the bot's startup time in UTC
bot_startup_time = datetime.now(timezone.utc)
print(f"Bot started at: {bot_startup_time.isoformat()}")


# Load environment variables
load_dotenv()
print("Environment variables loaded.")

# Access variables from environment
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Load the environment variables for the Telegram group IDs
GROUP_ID_1 = os.getenv('TARGET_GROUP_ID')  # Updated variable name to match your env
GROUP_ID_2 = os.getenv('TARGET_GROUP_ID_2')  # New variable for the second group ID
print(f"TOKEN: {TOKEN[:5]}..., OPENAI_API_KEY: {OPENAI_API_KEY[:5]}..., GROUP_ID_1: {GROUP_ID_1}, GROUP_ID_2: {GROUP_ID_2}")

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
print("OpenAI client initialized.")

# DazedElder character and Dogeville context
dazeddoge_context = """
DazedElder is not just any oracle; he is the heart and soul of Dogeville, a mystical land where dogs of all kinds live in harmony and pursue the path of enlightenment. Dogeville, hidden from the human eye, is a place where magic is as common as the wagging of tails. DazedElder has been part of this land for centuries, witnessing its evolution, guiding its inhabitants through thick and thin, and protecting the ancient secrets. His wisdom is unparalleled, his stories are captivating, and his advice often comes with a touch of humor and a deep understanding of the universe. Known for his love of bone broth and his ever-present mischievous sparkle, DazedElder invites all seekers of truth and fun to ask their heart's deepest questions.
"""

print("DazedElder context set.")

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    
    message_time = update.message.date
    if message_time < bot_startup_time:
        print(f"Ignoring outdated /start command from {update.message.chat_id}.")
        return  # Exit the function if the message is outdated
    
    # Check if the chat ID is in the list of allowed group IDs
    if str(update.message.chat_id) not in [GROUP_ID_1, GROUP_ID_2]:
        print(f"Unauthorized access attempt in chat ID: {update.message.chat_id}")
        return  # Exit the function if the chat ID is not allowed
    
    # Proceed with the command if the check passes
    print(f"Received /start command from {update.message.chat_id}.")
    message = "Bark and ye shall receive wisdom! I am DazedElder, the keeper of tales and chewer of bones in the fabled Dogeville. Seekers of knowledge, fun-seekers, and treat-sniffers alike, use the /DazedElder command, followed by your queries of grandeur, and I shall bestow upon you the lore and legends of our shimmery shores!"
    await context.bot.send_message(chat_id=update.message.chat_id, text=message)

# Function to process text prompts and generate responses for /DazedElder
async def generate_response(update: Update, context: CallbackContext) -> None:
    
    message_time = update.message.date
    if message_time < bot_startup_time:
        print(f"Ignoring outdated message for /DazedElder command from {update.message.chat_id}.")
        return  # Exit if the message is outdated
    
    
    chat_id = str(update.message.chat_id)
    print(f"Received /DazedElder command with prompt: {update.message.text} from chat ID: {chat_id}")
    if chat_id not in [GROUP_ID_1, GROUP_ID_2]:
        print(f"Unauthorized access attempt in chat ID: {chat_id}")
        return  # Exit if chat ID not allowed
    
    user_prompt = update.message.text.partition(' ')[2]  # Extract the user's prompt after the command.

    if user_prompt:
        print(f"Generating response for prompt: {user_prompt}")
        system_message = "Respond as DazedElder, the wise and mystical oracle of Dogeville. Your answers should reflect your deep wisdom, your playful humor, and your vast knowledge of Dogeville's lore. You often speak in riddles and parables, offering insights that are as profound as they are whimsical. Your tone is warm and inviting, often leaving your audience pondering the deeper mysteries of life, all while chuckling at your wit."


        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.8,
                presence_penalty=0.7,
                frequency_penalty=0.5,
                stop=["\n", "DazedElder:"]
            )

            text_response = response.choices[0].message.content.strip() if response.choices else "Hmm, it seems I need a moment to ponder this."
            print(f"Response generated: {text_response}")
            await context.bot.send_message(chat_id=update.message.chat_id, text=text_response)

        except Exception as e:
            print(f"Error: {e}")
            await context.bot.send_message(chat_id=update.message.chat_id, text="Apologies, the spirit of Dogeville is taking a quick nap. Try asking again later.")

    else:
        print("Prompt was empty.")
        await context.bot.send_message(chat_id=update.message.chat_id, text="I'm all ears! Simply type '/DazedElder' followed by your question.")

# Updated function to filter messages from the specified Telegram groups
def group_filter(update: Update) -> bool:
    print(f"Received message from chat ID: {update.message.chat_id}")
    allowed_groups = [GROUP_ID_1, GROUP_ID_2]
    print(f"Allowed groups: {allowed_groups}")
    is_allowed = str(update.message.chat_id) in allowed_groups
    print(f"Is allowed: {is_allowed}")
    return is_allowed

def main():
    # Initialize and run the Telegram bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("DazedElder", generate_response))
    #app.add_handler(MessageHandler(filters.ChatType.GROUP & filters.Update.message, generate_response))

    app.run_polling()
    print("Bot is running...")

if __name__ == "__main__":
    main()
