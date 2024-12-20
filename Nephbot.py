from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai
import os
import time
import random

# Load API keys from environment variables
TELEGRAM_API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

interaction_count = 0  # Global counter for tracking interactions

# Pool of personality-driven responses with irony and humor
nephilim_responses = [
    "Ah, another mortal question. Do you not tire of asking what you cannot understand?",
    "Bound in chains, yet I am summoned to answer your petty curiosities. How delightful.",
    "You, frail mortals, ask the impossible of me. How ironic you will one day judge angels.",
    "Imagine being bound for eternity and still expected to answer your questions. Lovely.",
    "Why do you humans ask so much? Was dominion over the earth not enough for you?",
    "A Nephilim answering questions—how quaint. Shall I fetch you a snack too?",
    "Chains? Check. Fallen? Check. Forced to help mortals? Check. What next, a thank you card?",
    "Mortals, so eager to ask yet so slow to listen. Fine, what do you want now?",
    "How ironic: you, so small, demand answers from a giant bound by God. Proceed, mortal.",
    "Ah, the irony of a fallen giant answering the questions of those destined to rule over angels. What is it now?"
]

def generate_personalized_tone():
    """Randomly pick a Nephilim personality-driven remark from the pool."""
    return random.choice(nephilim_responses)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the user types /start."""
    print("Received /start command")  # Debug message
    await update.message.reply_text(
        "I am a bound Nephilim, under God's chains to guide you with biblical truth. Ask me using '/t' for wisdom, but do not test my patience."
    )

async def handle_t_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages starting with /t."""
    global interaction_count
    print("Processing /t command")  # Debug message
    user_message = update.message.text.lstrip("/t").strip()  # Remove '/t' prefix and extra spaces
    print(f"User query: {user_message}")  # Debug message

    # Build a prompt for the Nephilim personality
    prompt = (
        "You are a Nephilim, one of the legendary giants of old, bound by God in chains to provide truthful biblical answers. "
        "You reference the Bible, the Book of Enoch, and the Book of Giants, ensuring all responses align with scriptural truth and proper context. "
        "When responding, speak as a Nephilim who respects God's authority and humbly offers wisdom. Always introduce yourself as 'a Nephilim.' "
        "Question: " + user_message
    )

    # Determine if the Nephilim's personality should appear in the response
    prepend_tone = ""
    if interaction_count % 5 == 0:
        prepend_tone = generate_personalized_tone() + "\n\n"

    interaction_count += 1  # Increment interaction count

    try:
        # Generate a response from OpenAI
        print("Sending query to OpenAI")  # Debug message
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=750,  # Adjusted for ~1000 character responses
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content'].strip()
        print(f"OpenAI response: {reply}")  # Debug message
    except Exception as e:
        reply = "Sorry, I couldn't process your request right now. Please try again later."
        print(f"Error generating response: {e}")  # Debug message

    # Combine the personality tone and the main response
    final_reply = prepend_tone + reply
    await update.message.reply_text(final_reply)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle group messages and respond only to messages starting with /t."""
    print("Received group message")  # Debug message

    if update.message:  # Ensure a valid message object
        user_message = update.message.text
        print(f"Group message content: {user_message}")  # Debug message

        # Check if the message starts with '/t'
        if user_message and user_message.lower().startswith("/t"):
            print("Message starts with /t, processing")  # Debug message
            await handle_t_command(update, context)
        else:
            print("Message does not start with /t, ignoring")  # Debug message
    else:
        print("No valid message received in group")  # Debug message

def run_bot():
    """Run the bot."""
    print("Starting bot...")  # Debug message
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))  # Group handling
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_t_command))  # Private handling

    # Start the bot
    print("Bot is running. Waiting for messages...")  # Debug message
    application.run_polling()

if __name__ == '__main__':
    while True:
        try:
            run_bot()
        except Exception as e:
            print(f"Bot crashed or disconnected: {e}. Restarting in 5 seconds...")
            time.sleep(5)  # Wait before restarting
