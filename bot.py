from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logic import *
import schedule
import threading
import time
from config import *

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['rating'])
def handle_rating(message):
    res = manager.get_rating()  # Placeholder for a function that retrieves the rating
    # Format the rating for display: | USER_NAME | COUNT_PRIZE |
    res = [f'| @{x[0]:<11} | {x[1]:<11}|\n{"_"*26}' for x in res]
    res = '\n'.join(res)
    res = f'|USER_NAME    |COUNT_PRIZE|\n{"_"*26}\n' + res
    bot.send_message(message.chat.id, res)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    prize_id = call.data
    user_id = call.message.chat.id

    # Placeholder for a function/variable that checks the number of winners
    if manager.get_winners_count(prize_id) <= 3: # This needs to be replaced with actual logic/variable
        res = manager.add_winner() # Placeholder for a function that adds a winner
        if res:
            img = manager.get_prize_img(prize_id) # Placeholder for a function that gets the image file name
            with open(f'img/{img}', 'rb') as photo:
                bot.send_photo(user_id, photo, caption="Congratulations! You received the image!")
        else:
            bot.send_message(user_id, 'You have already received the image!')
    else:
        bot.send_message(user_id, "Unfortunately, you didn't make it in time to get the image! Try next time!)")
def gen_markup(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Получить!", callback_data=id))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    prize_id = call.data
    user_id = call.message.chat.id

    img = manager.get_prize_img(prize_id)
    with open(f'img/{img}', 'rb') as photo:
        bot.send_photo(user_id, photo)


def send_message():
    prize_id, img = manager.get_random_prize()[:2]
    manager.mark_prize_used(prize_id)
    manager.hide_img(img)
    for user in manager.get_users():
        with open(f'hidden_img/{img}', 'rb') as photo:
            bot.send_photo(user, photo, reply_markup=gen_markup(id = prize_id))
        

def shedule_thread():
    schedule.every().minute.do(send_message) # Здесь ты можешь задать периодичность отправки картинок
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    if user_id in manager.get_users():
        bot.reply_to(message, "Ты уже зарегестрирован!")
    else:
        manager.add_user(user_id, message.from_user.username)
        bot.reply_to(message, """Привет! Добро пожаловать! 
Тебя успешно зарегистрировали!
Каждый час тебе будут приходить новые картинки и у тебя будет шанс их получить!
Для этого нужно быстрее всех нажать на кнопку 'Получить!'

Только три первых пользователя получат картинку!)""")
        


def polling_thread():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    manager = DatabaseManager(DATABASE)
    manager.create_tables()

    polling_thread = threading.Thread(target=polling_thread)
    polling_shedule  = threading.Thread(target=shedule_thread)

    polling_thread.start()
    polling_shedule.start()
  
