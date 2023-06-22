import logging
import os

import requests
from dotenv import load_dotenv
from telebot import TeleBot


load_dotenv()



API_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "http://127.0.0.1:8000/api/tasks/"

bot = TeleBot(API_TOKEN)

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот для управления задачами. Используй команды"
        " /create, /list, /view, /update, /complete, /delete для взаимодействия со списком задач."
        " При заполнении полей title и description используй нижние подчеркивания вместо пробелов",
    )


@bot.message_handler(commands=["create"])
def create_task(message):
    command_args = message.text.split()[1:]
    if len(command_args) != 3:
        bot.reply_to(
            message,
            "Некорректный формат команды. Используй /create <title> <description> <due_date>. "
            "Убедись, что используешь '_' вместо пробелов",
        )
        return

    title, description, due_date = command_args
    data = {
        "title": title,
        "description": description,
        "due_date": due_date,
        "completed": False,
    }

    try:
        response = requests.post(BASE_URL, data=data)
        if response.status_code == 201:
            bot.reply_to(message, "Задача успешно создана!")
        else:
            bot.reply_to(
                message,
                "Ошибка при создании задачи. Убедитесь, что ввели данные в верном формате. "
                "Пример: <Задача> <Описание задачи> 2023-10-22. "
                "Убедитесь, что используете '_' вместо пробелов",
            )
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при создании задачи: {str(e)}")


@bot.message_handler(commands=["list"])
def list_tasks(message):
    command_args = message.text.split()[1:]
    page = command_args[0] if command_args else 1
    limit = command_args[1] if len(command_args) > 1 else 10

    try:
        response = requests.get(BASE_URL, params={"page": page, "limit": limit})
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task_list = "\n".join(
                    f"{task['id']}. {task['title']}" for task in tasks
                )
                bot.reply_to(message, f"Список задач:\n{task_list}")
            else:
                bot.reply_to(message, "Список задач пуст.")
        else:
            bot.reply_to(message, "Ошибка при получении списка задач.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при получении списка задач: {str(e)}")


@bot.message_handler(commands=["view"])
def view_task(message):
    command_args = message.text.split()[1:]
    if not command_args:
        bot.reply_to(
            message, "Некорректный формат команды. Используй /view <task_id>."
        )
        return

    task_id = command_args[0]

    try:
        response = requests.get(f"{BASE_URL}{task_id}")
        if response.status_code == 200:
            task = response.json()
            bot.reply_to(
                message,
                f"Задача {task['id']}:\n"
                f"Название: {task['title']}\n"
                f"Описание: {task['description']}\n"
                f"Дата выполнения: {task['due_date']}\n"
                f"Статус: {'Завершена' if task['completed'] else 'Не завершена'}",
            )
        elif response.status_code == 404:
            bot.reply_to(message, "Задача не найдена.")
        else:
            bot.reply_to(message, "Ошибка при получении информации о задаче.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при получении информации о задаче: {str(e)}")


@bot.message_handler(commands=["update"])
def update_task(message):
    command_args = message.text.split()[1:]
    if len(command_args) != 4:
        bot.reply_to(
            message,
            "Некорректный формат команды. Используй /update <task_id> <title> <description> <due_date>."
            " Убедитесь, что используете '_' вместо пробелов",
        )
        return

    task_id, title, description, due_date = command_args
    data = {
        "title": title,
        "description": description,
        "due_date": due_date,
    }

    try:
        response = requests.put(f"{BASE_URL}{task_id}", data=data)
        if response.status_code == 200:
            bot.reply_to(message, f"Задача {task_id} успешно обновлена!")
        elif response.status_code == 404:
            bot.reply_to(message, "Задача не найдена.")
        else:
            bot.reply_to(message, "Ошибка при обновлении задачи.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при обновлении задачи: {str(e)}")


@bot.message_handler(commands=["complete"])
def complete_task(message):
    command_args = message.text.split()[1:]
    if not command_args:
        bot.reply_to(
            message, "Некорректный формат команды. Используй /complete <task_id>."
        )
        return

    task_id = command_args[0]

    try:
        response = requests.patch(f"{BASE_URL}{task_id}", data={"completed": True})
        if response.status_code == 200:
            bot.reply_to(message, f"Задача {task_id} отмечена как выполненная!")
        elif response.status_code == 404:
            bot.reply_to(message, "Задача не найдена.")
        else:
            bot.reply_to(message, "Ошибка при обновлении статуса задачи.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при обновлении статуса задачи: {str(e)}")


@bot.message_handler(commands=["delete"])
def delete_task(message):
    command_args = message.text.split()[1:]
    if not command_args:
        bot.reply_to(
            message, "Некорректный формат команды. Используй /delete <task_id>."
        )
        return

    task_id = command_args[0]

    try:
        response = requests.delete(f"{BASE_URL}{task_id}")
        if response.status_code == 204:
            bot.reply_to(message, f"Задача {task_id} успешно удалена!")
        elif response.status_code == 404:
            bot.reply_to(message, "Задача не найдена.")
        else:
            bot.reply_to(message, "Ошибка при удалении задачи.")
    except requests.exceptions.RequestException as e:
        bot.reply_to(
            message, "Ошибка при выполнении запроса. Пожалуйста, попробуйте позже."
        )
        logging.error(f"Ошибка при удалении задачи: {str(e)}")


bot.polling()
