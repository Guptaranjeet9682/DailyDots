import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Configuration ---
# Get the bot token from an environment variable for security
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# The file to store all user data
DATA_FILE = "user_data.json"

# --- Data Management Functions ---
def load_data():
    """Loads user data from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or corrupted, return an empty dictionary
            return {}
    return {}

def save_data(data):
    """Saves the given data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Command Handlers ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    user = update.effective_user
    welcome_text = f"""
👋 Hello {user.first_name}!

I'm your Personal Productivity Bot 🤖

Here's what I can do:
✅ /add - Add a new task
✅ /tasks - Show your tasks
✅ /done - Mark a task as done
✅ /delete - Delete a task
✅ /clear - Clear all tasks
✅ /help - Show this help message

Let's get productive! 🚀
    """
    await update.message.reply_text(welcome_text)

async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adds a new task to the user's list."""
    try:
        user_id = str(update.effective_user.id)
        task_text = " ".join(context.args)

        if not task_text:
            await update.message.reply_text("Please provide a task. Example: /add Buy groceries")
            return

        data = load_data()
        if user_id not in data:
            data[user_id] = {"tasks": []}

        # Find the next available ID
        new_task_id = len(data[user_id]["tasks"]) + 1

        data[user_id]["tasks"].append({
            "id": new_task_id,
            "text": task_text,
            "done": False,
            "created_at": str(datetime.now())
        })

        save_data(data)
        task_count = len(data[user_id]['tasks'])
        await update.message.reply_text(f"✅ Task added! You now have {task_count} task(s).")
    except Exception as e:
        print(f"Error in add_task_command: {e}")
        await update.message.reply_text("An error occurred while adding the task. Please try again.")

async def my_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays all of the user's tasks."""
    try:
        user_id = str(update.effective_user.id)
        data = load_data()

        if user_id not in data or not data[user_id]["tasks"]:
            await update.message.reply_text("📝 You don't have any tasks yet! Use /add to create one.")
            return

        tasks_text = "📋 Your Tasks:\n\n"
        for task in data[user_id]["tasks"]:
            status_icon = "✅" if task["done"] else "⏳"
            tasks_text += f"{task['id']}. {status_icon} {task['text']}\n"

        await update.message.reply_text(tasks_text)
    except Exception as e:
        print(f"Error in my_tasks_command: {e}")
        await update.message.reply_text("An error occurred while loading your tasks. Please try again.")

async def done_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Marks a specific task as done."""
    try:
        user_id = str(update.effective_user.id)
        task_id_str = context.args[0]
        task_id = int(task_id_str)

        data = load_data()

        if user_id not in data or not data[user_id]["tasks"]:
            await update.message.reply_text("You don't have any tasks to mark as done!")
            return

        task_found = False
        for task in data[user_id]["tasks"]:
            if task["id"] == task_id:
                if task["done"]:
                    await update.message.reply_text(f"👍 Task {task_id} was already marked as done.")
                else:
                    task["done"] = True
                    save_data(data)
                    await update.message.reply_text(f"🎉 Great job! Task {task_id} marked as done!")
                task_found = True
                break
        
        if not task_found:
            await update.message.reply_text("Task ID not found!")

    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid task ID. Example: /done 1")
    except Exception as e:
        print(f"Error in done_task_command: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

async def delete_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deletes a specific task from the list."""
    try:
        user_id = str(update.effective_user.id)
        task_id_to_delete = int(context.args[0])

        data = load_data()

        if user_id not in data or not data[user_id]["tasks"]:
            await update.message.reply_text("You have no tasks to delete!")
            return
        
        # Filter out the task to be deleted
        original_task_count = len(data[user_id]["tasks"])
        data[user_id]["tasks"] = [task for task in data[user_id]["tasks"] if task["id"] != task_id_to_delete]

        if len(data[user_id]["tasks"]) == original_task_count:
            await update.message.reply_text(f"Task with ID {task_id_to_delete} not found.")
            return

        # Re-number the remaining tasks to keep IDs sequential
        for index, task in enumerate(data[user_id]["tasks"], 1):
            task["id"] = index
        
        save_data(data)
        await update.message.reply_text(f"🗑️ Task {task_id_to_delete} has been deleted.")

    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid task ID. Example: /delete 1")
    except Exception as e:
        print(f"Error in delete_task_command: {e}")
        await update.message.reply_text("An error occurred while deleting the task.")

async def clear_tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears all tasks for the user."""
    try:
        user_id = str(update.effective_user.id)
        data = load_data()

        if user_id in data and data[user_id]["tasks"]:
            task_count = len(data[user_id]["tasks"])
            data[user_id]["tasks"] = []
            save_data(data)
            await update.message.reply_text(f"🧹 All clear! Deleted {task_count} tasks.")
        else:
            await update.message.reply_text("You have no tasks to clear!")
    except Exception as e:
        print(f"Error in clear_tasks_command: {e}")
        await update.message.reply_text("An error occurred while clearing your tasks.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command."""
    help_text = """
📋 **Productivity Bot Help**

Here are the available commands:
• /start - Start the bot
• /add [your task] - Add a new task
• /tasks - Show all your tasks
• /done [task ID] - Mark a task as completed
• /delete [task ID] - Delete a specific task
• /clear - Delete all of your tasks
• /help - Show this help message

Example:
`/add Buy milk and bread`
`/done 1`
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# --- Main Bot Setup ---
def main():
    """Starts the bot."""
    print("Bot is starting...")
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add", add_task_command))
    application.add_handler(CommandHandler("tasks", my_tasks_command))
    application.add_handler(CommandHandler("done", done_task_command))
    application.add_handler(CommandHandler("delete", delete_task_command))
    application.add_handler(CommandHandler("clear", clear_tasks_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start the Bot
    print("✅ Productivity Bot is running and polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
