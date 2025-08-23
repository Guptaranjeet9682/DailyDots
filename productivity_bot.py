import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot token - replace with your actual token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# File to store user data
DATA_FILE = "user_data.json"

# Load user data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
👋 नमस्ते {user.first_name}! 

I'm your Personal Productivity Bot 🤖

Here's what I can do:
✅ /addtask - Add a new task
✅ /mytasks - Show your tasks
✅ /donetask - Mark task as done
✅ /deltask - Delete a task
✅ /cleartasks - Clear all tasks
✅ /help - Show help

Let's get productive! 🚀
    """
    await update.message.reply_text(welcome_text)

# Add task command
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    task_text = " ".join(context.args)
    
    if not task_text:
        await update.message.reply_text("Please provide a task. Example: /addtask Buy groceries")
        return
    
    data = load_data()
    if user_id not in data:
        data[user_id] = {"tasks": []}
    
    task_id = len(data[user_id]["tasks"]) + 1
    data[user_id]["tasks"].append({
        "id": task_id,
        "text": task_text,
        "done": False,
        "created_at": str(datetime.now())
    })
    
    save_data(data)
    await update.message.reply_text(f"✅ Task added! You now have {len(data[user_id]['tasks'])} task(s).")

# Show tasks command
async def my_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id not in data or not data[user_id]["tasks"]:
        await update.message.reply_text("📝 You don't have any tasks yet! Use /addtask to create one.")
        return
    
    tasks_text = "📋 Your Tasks:\n\n"
    for task in data[user_id]["tasks"]:
        status = "✅" if task["done"] else "⏳"
        tasks_text += f"{task['id']}. {status} {task['text']}\n"
    
    await update.message.reply_text(tasks_text)

# Mark task as done
async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id not in data or not data[user_id]["tasks"]:
        await update.message.reply_text("No tasks to mark as done!")
        return
    
    try:
        task_id = int(context.args[0])
        for task in data[user_id]["tasks"]:
            if task["id"] == task_id:
                task["done"] = True
                save_data(data)
                await update.message.reply_text(f"🎉 Task {task_id} marked as done!")
                return
        
        await update.message.reply_text("Task not found!")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid task ID. Example: /donetask 1")

# Delete task command
async def del_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id not in data or not data[user_id]["tasks"]:
        await update.message.reply_text("No tasks to delete!")
        return
    
    try:
        task_id = int(context.args[0])
        data[user_id]["tasks"] = [task for task in data[user_id]["tasks"] if task["id"] != task_id]
        
        # Re-number tasks
        for idx, task in enumerate(data[user_id]["tasks"], 1):
            task["id"] = idx
        
        save_data(data)
        await update.message.reply_text(f"🗑️ Task {task_id} deleted!")
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid task ID. Example: /deltask 1")

# Clear all tasks
async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id in data and data[user_id]["tasks"]:
        task_count = len(data[user_id]["tasks"])
        data[user_id]["tasks"] = []
        save_data(data)
        await update.message.reply_text(f"🧹 Cleared {task_count} tasks!")
    else:
        await update.message.reply_text("No tasks to clear!")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 **Productivity Bot Help**

Commands:
• /start - Start the bot
• /addtask [text] - Add a new task
• /mytasks - Show all your tasks
• /donetask [id] - Mark task as done
• /deltask [id] - Delete a task
• /cleartasks - Clear all tasks
• /help - Show this help

Example:
/addtask Buy milk
/donetask 1
    """
    await update.message.reply_text(help_text)

# Main function
def main():
    # Create the Application with modern syntax
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("mytasks", my_tasks))
    application.add_handler(CommandHandler("donetask", done_task))
    application.add_handler(CommandHandler("deltask", del_task))
    application.add_handler(CommandHandler("cleartasks", clear_tasks))
    application.add_handler(CommandHandler("help", help_command))
    
    print("Productivity Bot is running...")
    
    # Start polling with modern method
    application.run_polling()

if __name__ == "__main__":
    main()
