
import telebot
import config
import random
import datetime
from datetime import time
from telebot import types
from db import DataBase
from pyqiwip2p import QiwiP2P
import bomb

now = datetime.datetime.now()#Текущая дата
nows = ("{}.{}.{}  {}:{}".format(now.day, now.month, now.year, now.hour, now.minute))
date_for_db = ("{}-{}-{}  {}:{}".format(now.day, now.month, now.year, now.hour, now.minute+10))
date_for_bomb = ("{}-{}-{}-{}.{}".format(now.day, now.month, now.year, now.hour, now.minute-10))
update_date = ("{}-{}-{}-{}.{}".format(now.day, now.month, now.year, now.hour, now.minute))
PayQiwi = QiwiP2P(auth_key=config.QIWI_TOKEN)
db = DataBase(config.DB)
bot = telebot.TeleBot(config.API_TOKEN)
def isNumber(_str):
    try:
        int(_str)
        return True
    except Exception as e:
        return False

def num(phone):
    if ((phone[0:2] == "+7" and len(phone[1:]) == 11) or (phone[0:4] == '+380' and len(phone[4:]) == 12)):
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start(m):
    if not db.user_exist(m.from_user.id):
        db.add_user(m.from_user.id)
        bot.send_message(m.chat.id, f'<strong>Приветствуем тебя у нас на портале</strong>\nТы успешно занесен в нашу базу!\nНажми /help чтобы перейти к основному меню', parse_mode="html")
       
        
    else:
        msg = bot.send_message(m.chat.id, "<strong>Нажмите</strong> <b>/help\n</b><i>Чтобы перейти к основному меню</i>", parse_mode="html")
        
@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact != None:
        db.set_userPhone(message.chat.id, message.contact.phone_number)
        
        
@bot.message_handler(content_types=["text"])
def handle_text(message):
    
    if message.text.strip() == "/help":
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        Info_user = types.KeyboardButton("👤Личная информация")
        what_know_how = types.KeyboardButton("ℹ️Что я умею?")
        Spam = types.KeyboardButton("💣Запустить бомбер")
        markup.row(Info_user, Spam)
        markup.row(what_know_how)
        
        bot.send_message(message.chat.id, '<b>Нажми: </b>', reply_markup=markup, parse_mode='html')
    
    elif message.text.strip() == '👤Личная информация' :
        
        markup2 = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("💵Пополнить баланс💵", callback_data="top_up")
        markup2.add(item1)
        answer = f"<b>Мой аккаунт</b>\n<i>Вся необходимая информация о вашем профиле\n\n</i><strong>Тебя зовут:</strong> {message.from_user.first_name}\n<strong>Твой ID:</strong> {message.from_user.id}\n<strong>Ваш логин:</strong> @{message.from_user.username}\n<strong>Баланс:</strong> {db.user_money(message.from_user.id)} руб."
        bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup= markup2)
        contact = message.contact
        
    
    elif message.text.strip() == "ℹ️Что я умею?":
        answer = "<strong>Пока что я сам не знаю(\nНо в скором времени здесь будет полная информация обо мне</strong>"
        bot.send_message(message.chat.id, answer, parse_mode='html')
    elif message.text.strip() == "💣Запустить бомбер":
        markup_s = types.InlineKeyboardMarkup(row_width=3)
        markup_s.add(types.InlineKeyboardButton("Начать бомбить", callback_data="bomb"))
        bot.send_message(message.chat.id, "<i>Введите номер телефона жертвы:\nНачиная с </i><b>+7</b> <i>или</i> <b>+380</b><i>!!!</i>", parse_mode='html',reply_markup=markup_s)

    
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "top_up":
        # p = open("img.jpg", 'rb')#Добавляем фото и открываем его# Посылаем фото боту для отправки и подписываем его caption
        bot.answer_callback_query(call.id, "Пополнение баланса от 10 рублей!", show_alert=True)#Уведомление пользователю
        # bot.send_message(call.from_user.id, f"Введите сумму пополнения💰🤑:")
        msg = bot.send_message(call.from_user.id, "Введите сумму пополнения💰🤑:")
        bot.register_next_step_handler(msg, popolnenie_balansa)
        
    elif call.data == "top_ups":
        # p = open("img.jpg", 'rb')#Добавляем фото и открываем его# Посылаем фото боту для отправки и подписываем его caption
        bot.answer_callback_query(call.id, "Пополнение баланса от 10 рублей!", show_alert=True)#Уведомление пользователю
        # bot.send_message(call.from_user.id, f"Введите сумму пополнения💰🤑:")
        msg = bot.send_message(call.from_user.id, "Введите сумму пополнения💰🤑:")
        bot.register_next_step_handler(msg, popolnenie_balansa)
        
    elif "check_" in call.data:
        bill = call.data[6:]
        info = db.get_check(bill_id=bill)
        if info != False:
            try:
                if (PayQiwi.check(bill_id=bill).status) == "PAID":
                    user_money = db.user_money(call.from_user.id)
                    money = int(info[2])
                    db.set_money(call.from_user.id, user_money+money)
                    db.set_date(call.from_user.id, "Оплачен")
                    date_check = "Оплачен"
                    db.add_checks(call.from_user.id, money, nows, date_check)
                    bot.send_message(call.from_user.id, "✅Счет успешно пополнен)👌")
                    
                else:
                    bot.send_message(call.from_user.id, "❌Счет не оплачен❌")
            except Exception as e:
                print(e)
    
        else:
            bot.send_message(call.from_user.id, "🤷‍♂️Счет не найден🤷‍♂️")
    elif call.data == "bomb":
        msg = bot.send_message(call.from_user.id, "Вводи номер📲:")
        bot.register_next_step_handler(msg, doomb_number)
    elif call.data == "menu":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='вы вернулись в главное меню', reply_markup=start("\start"))
        
def doomb_number(message):
    spam(message)
    
            
def popolnenie_balansa(message):
    bot_mess(message)
    

def bot_mess(message):
    if isNumber(message.text):
        message_money = int(message.text)#Образали строки начали идти с 0 элемента и забили на последний
        if message_money >= 10:
            date_check = "Не оплачен"
            comment = str(message.from_user.id) + "_" + str(random.randint(1000, 6000))
            bill = PayQiwi.bill(amount=message_money, lifetime = 10, comment = comment)
            db.add_check(message.from_user.id, message_money, bill.bill_id, nows, date_check)
            markup = types.InlineKeyboardMarkup(row_width=3)
            items = types.InlineKeyboardButton(text="⏳Оплатить⏳", url=bill.pay_url)
            items2 = types.InlineKeyboardButton(text="🧮Проверить оплату🧮", callback_data="check_"+bill.bill_id)
            markup.add(items)
            markup.add(items2)
            bot.send_message(message.chat.id, f"💲Пополнение баланса на сумму {message_money} рублей💲:", reply_markup=markup)   
        else:
            bot.send_message(message.chat.id, "⚠️Пополнение баланса от 10 рублей⚠️\n<i>Нажмите</i> <b>Пополнить баланс</b> <i>еще раз, чтобы ввести сумму пополнения заново</i>", parse_mode="html")
    
    else:
        bot.send_message(message.chat.id, "Вводите только цифры!\n<i>Нажмите</i> <b>Пополнить баланс</b> <i>еще раз, чтобы ввести сумму пополнения заново</i>", parse_mode="html")
        
def spam_exit(message):
    bot.send_message(message.chat.id, "Бомбер уже запущен, ошидайте завершения спама")
            
def spam(message):
    try:
        if num(message.text) != False:
            phone = message.text
            
            bot.send_message(message.chat.id, "Номер введен корректно✅")
            user_money = db.user_money(message.from_user.id)
            data = db.data_user_zapusk(message.chat.id)
            if user_money >= 5:
                db.add_data_zapuska(update_date, message.chat.id)
                bot.send_message(message.chat.id, "Бомбер запущен на 10 минут)")
                db.set_money(message.from_user.id, user_money-5)
                bomb.bomb(phone)
                bot.send_message(message.from_user.id, f"Спам номера <strong>{phone}</strong> закончен", parse_mode="html")
            else:
                mar = types.InlineKeyboardMarkup()
                mar.add(types.InlineKeyboardButton("💳Пополнить баланс💳", callback_data="top_ups"))
                bot.send_message(message.chat.id, "Недостаточно средств\n<b>Один запуск стоит 5 рублей</b>", parse_mode="html", reply_markup=mar)
      
        else:
            bot.send_message(message.chat.id, "🚫Номер телефона введен не верно🚫\n<i>Нажмите</i> <b>Начать бомбить</b> <i>еще раз,чтобы прейти к вводу номера</i>", parse_mode="html")
            
    except Exception as e:print(e)
if __name__ == "__main__":
    bot.polling(none_stop=True)