import logging
import threading
import xlsxwriter
import requests
import schedule
import telegram.ext
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler
from for_DBwork import DB

# Импорт необходимых библиотек
# Запускаем логгирование
logging.basicConfig(filename='logging.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
                    )

logger = logging.getLogger(__name__)
TOKEN = '5355485794:AAGBNp_ZMuEw8vK1t9UiuuDOV8yOY0OQN_E'  # токен бота
# TOKEN = '5342995443:AAEBqyRLrd5AmHEEhCNLyfHVy3td3Qvw-Ec' # мой токен
SUPER_PASSWORD = 'Admin777'  # пароль для админа
BD = DB()  # подключение к БД


def get_date_add(update, context):  # получение дат(ы) для добавления
    date = update.message.text.split(', ')
    for i in date:
        BD.add_mailing(context.user_data['text'].capitalize(), i, context.user_data['company'].capitalize())
    update.message.reply_text('Успешно! Уведомления ждут своей отправки.')
    return ConversationHandler.END


def start(update, context):  # старт
    update.message.reply_text('''Здравствуйте! Я смогу ответить на возникшие у Вас вопросы,
но для начала нужно пройти регистрацию. Напишите, пожалуйста, Вашу роль.
Например: Klient или Клиент''')
    return 1


def stop_new_mailing(update, context):  # завершение
    update.message.reply_text('Добавление уведомления остановлено.')
    return ConversationHandler.END


def info(update, context):  # присвоение роли пользователя при регистрации
    a = update.message.text.capitalize()
    logger.info(' '.join([a, 'Admin', str(a == 'Admin')]))
    if a == 'Admin' or a == 'Админ':
        context.user_data['Post'] = 1
        update.message.reply_text('''Для того чтобы стать администратором,
нужно ввести выданный Вам пароль:
Например: 0000''')
        return 2
    elif a == 'Klient' or a == 'Клиент':
        context.user_data['Post'] = 0
        update.message.reply_text('''Готов произвести регистрацию.
Введите Ваше ФИО через пробел.
Например: Иванов Иван Иванович''')
        return 3


def edit_post_input_post(update, context):  # присвоение роли пользователя
    a = update.message.text.capitalize()
    logger.info(' '.join([a, 'Admin', str(a == 'Admin')]))
    if a == 'Admin' or a == 'Админ':
        context.user_data['Post'] = 1
    elif a == 'Klient' or a == 'Клиент':
        context.user_data['Post'] = 0
    update.message.reply_text('''Для того чтобы сменить роль,
нужно ввести выданный Вам пароль:
Например: 0000''')
    return 2


def edit_post_input_password(update, context):  # функция проверки суперпароля
    a = update.message.text
    logger.info(' '.join([a, SUPER_PASSWORD, str(a == SUPER_PASSWORD)]))
    if a == SUPER_PASSWORD:
        update.message.reply_text('Готов произвести смену роли...')
        BD.edit_user_post(context.user_data['Post'], str(update.message.from_user.id))
        update.message.reply_text('Успешно! Ваша роль изменена.')
        return ConversationHandler.END
    else:
        update.message.reply_text('''Для того чтобы сменить роль,
нужно ввести выданный Вам пароль:
Например: 0000''')
        return 2


def get_date_del(update, context):  # удаление даты
    date = update.message.text.split(', ')
    for i in date:
        BD.delete_mailing(context.user_data['text'].capitalize(), i, context.user_data['company'].capitalize())
    update.message.reply_text('Успешно! Дата удалена.')
    return ConversationHandler.END


def stop_reg(update, context):  # завершение
    update.message.reply_text('Регистрация приостановлена.')
    context.user_data.clear()
    return ConversationHandler.END


def stop_del_mailing(update, context):  # завершение
    update.message.reply_text('Удаление рассылки остановлено.')
    return ConversationHandler.END


def password_request(update, context):  # функция проверки суперпароля, используемого для админов
    a = update.message.text
    logger.info(' '.join([a, SUPER_PASSWORD, str(a == SUPER_PASSWORD)]))
    if a == SUPER_PASSWORD:
        update.message.reply_text('''Готов произвести регистрацию.
Введите Ваше ФИО через пробел.
Например: Иванов Иван Иванович''')
        return 3
    else:
        context.user_data.clear()
        update.message.reply_text('''Здравствуйте! Я смогу ответить на возникшие у Вас вопросы,
        но для начала нужно пройти регистрацию. Напишите, пожалуйста, Вашу роль.
        Например: Klient или Клиент''')
        return 1


def add_question(update, context):  # получение вопроса
    update.message.reply_text('Введите вопрос, который нужно добавить/редактировать/удалить.')
    return 1


def entering_info(update, context):  # добавление ФИО
    context.user_data['ФИО'] = update.message.text
    # добавление пользователя

    fio = context.user_data['ФИО'].split()
    logger.info(str(fio) + str(context.user_data['Post']))
    if len(fio) == 3:
        BD.add_user(fio[0].capitalize(), fio[1].capitalize(), fio[2].capitalize(), context.user_data['Post'],
                    str(update.message.from_user.id))
    elif len(fio) == 2:
        BD.add_user(fio[0].capitalize(), fio[1].capitalize(), '', context.user_data['Post'],
                    str(update.message.from_user.id))
    else:
        update.message.reply_text('Неверно введены данные.')
        update.message.reply_text('''Готов произвести регистрацию.
        Введите Ваше ФИО через пробел.
        Например: Иванов Иван Иванович''')
        return 3
    update.message.reply_text('Регистрация прошла успешно!',
                              reply_markup=markup)
    if context.user_data['Post'] == 0:
        reg_in_company(update, fio[1].capitalize())
    context.user_data.clear()
    return ConversationHandler.END


def add_answer(update, context):  # добавление ответа на вопрос
    context.user_data['question'] = update.message.text.capitalize()
    update.message.reply_text(f'{BD.get_user_name(str(update.message.from_user.id))}, введите ответ на вопрос.')
    return 2


def reg_in_company(update, context):  # регистрация в компании
    update.message.reply_text(f'''{BD.get_user_name(str(update.message.from_user.id))}, теперь Вы можете вступить в компанию.
Для этого напишите или нажмите на /reg_company''')


def creating_question(update, context):  # создание вопроса
    context.user_data['answer'] = update.message.text.capitalize()
    update.message.reply_text(
        f'{BD.get_user_name(str(update.message.from_user.id))}, введите компанию, участники которой могут задать вопрос.')
    return 3


def linking_company(update, context):  # регистрация в компании
    logger.info('привязка к компании')
    update.message.reply_text(
        f'''{BD.get_user_name(str(update.message.from_user.id))}, введите название компании, в которую хотите вступить.''')
    return 1


def stop_question_add(update, context):  # завершение
    update.message.reply_text('Добавление/реадктирование/удаление вопроса остановлено.')
    return ConversationHandler.END


def get_name_company_password(update, context):  # регистрация в компании
    name_company = update.message.text.capitalize()
    context.user_data['NameCompany'] = name_company
    a = BD.check_company(name_company)
    if not a:
        update.message.reply_text('''Произошла ошибка: Компании с таким
названием не существует.
Проверьте введенные данные.''')
        update.message.reply_text(
            f'''{BD.get_user_name(str(update.message.from_user.id))}, введите название компании, в которую хотите вступить.''')
        return 1
    context.user_data['PasswordCompany'] = BD.get_company_password(context.user_data['NameCompany'])
    update.message.reply_text('Компания найдена. Введите пароль.')
    return 2


def write_question_add(update, context):  # добавление вопроса
    a = update.message.text.capitalize()
    BD.add_question(context.user_data['question'].capitalize(), context.user_data['answer'].capitalize(), a)


def get_pass(update, context):  # регистрация в компании
    if context.user_data['PasswordCompany'] != update.message.text:
        update.message.reply_text('Возникла ошибка: введен неверный пароль.')
        update.message.reply_text('Компания найдена. Введите пароль.')
        return 1
    BD.remove_user_company(str(update.message.from_user.id), context.user_data['NameCompany'])
    update.message.reply_text(f'{BD.get_user_name(str(update.message.from_user.id))}, Вы успешно вступили компанию.')
    return ConversationHandler.END


def stop_linking(update, context):  # завершение
    update.message.reply_text('''Теперь Вы можете вступить в компанию.
Для этого напишите или нажмите на /reg_company''')
    return ConversationHandler.END


def checking_status(update):  # проверка роли пользователя
    return False if BD.get_user_post(update.message.from_user.id) == 0 else True


def unbinding_company(update, context):  # выход из компании
    BD.remove_user_company(str(update.message.from_user.id), '')
    update.message.reply_text(f'{BD.get_user_name(str(update.message.from_user.id))}, Вы вышли из компании.')


def get_question(update, context):  # получить ответ
    company = BD.get_user_company(str(update.message.from_user.id))
    if company == None:
        if BD.get_user_post(str(update.message.from_user.id)) == 0:
            update.message.reply_text(
                f'{BD.get_user_name(str(update.message.from_user.id))}, Вы не можете получить ответ, так как не состоите в компании.')
        else:
            update.message.reply_text(f'''{BD.get_user_name(str(update.message.from_user.id))}, Вы - администратор! Уверен, ответы на
все интересующие вопросы Вы знаете сами)''')
    else:
        if update.message.text.capitalize() in list(map(lambda i: i[1][0], BD.get_questions(company))):
            update.message.reply_text(str(BD.get_answer(update.message.text.capitalize(), company)))
        else:
            update.message.reply_text('Извините, вопрос не найден.')


def input_name_company(update, context):  # создание компании
    if not checking_status(update):
        update.message.reply_text('Для создания компании вы должны быть администратором.')
        return ConversationHandler.END
    update.message.reply_text('Введите будущее название компании.')
    return 1


def input_password_company(update, context):  # создание компании
    context.user_data['title'] = update.message.text
    update.message.reply_text('Введите пароль компании для входа пользователей.')

    return 2


def input_get_telephone(update, context):  # создание компании
    context.user_data['password'] = update.message.text
    update.message.reply_text('Введите контактный телефон владельца компании (Ваш).')
    return 3


def creating_company(update, context):  # создание компании
    BD.add_company(context.user_data['title'], update.message.text, context.user_data['password'])
    update.message.reply_text('Успешно! Компания создана, а Вы её администратор.')
    context.user_data.clear()
    return ConversationHandler.END


def stop_new_company(update, context):  # завершение
    update.message.reply_text('Остановка создания компании.')
    return ConversationHandler.END


def delete_company(update, context):  # удаление компании
    if not checking_status(update):
        update.message.reply_text('Для создания компании Вы должны быть администратором.')
        return
    update.message.reply_text('''Введите название компании, которую 
хотите удалить. ВНИМАНИЕ: это действие отменить будет невозможно.''')
    return 1


def delete_comp(update, context):  # удаление компании
    a = update.message.text.capitalize()
    BD.delete_company(a)
    update.message.reply_text('Компания удалена.')


def helps(update, context):  # помощь
    if checking_status(update):
        update.message.reply_text(
            f'Привет, уважаемый пользователь, {BD.get_user_name(str(update.message.from_user.id))}, Ваша роль - Admin.\n'
            'Доступные Вам функции:\n'
            '/geocoder - Узнать адрес компании\n'
            '/get_xlsx_file - получить Excel таблицу со всеми данными для просмотра и диагностики\n'
            '/stop используется для остановки любого процесса, в котором бы вы не находились.\n '
            '/creating_company используется для создания новой компании.\n'
            'Данные, используемые при создании компании: название компании, её уникальный '
            'пароль, номер телефона.\n '
            '/edit_post изменить/выбрать роль.\n'
            '/delete_company используется для удаления уже существующей компании. Для удаления '
            'необходимо только название.\n '
            '/add_mailing используется для создания новой рассылки. Для её создания необходимо '
            'несколько элементов: компания, текст, даты отправления.\n '
            '/delete_mailing используется для удаления рассылки. Для её удаления необходимо '
            'несколько элементов: компания, текст, дата отправления.\n'
            '/add_question используется для создания нового вопроса. Для его создания необходимо '
            'несколько элементов: компания, текст вопроса, текст ответа.\n'
            '/redact_question используется для редактирования существующего вопроса. Для его '
            'редактирования необходимо'
            'несколько элементов: компания, текст вопроса, изменённый текст ответа.\n'
            '/delete_question используется для удаления вопроса. Для его удаления необходимо '
            'несколько элементов: компания, текст вопроса, текст ответа.\n'
            'Приятного использования!')
    else:
        update.message.reply_text(
            f'Привет, уважаемый пользователь, {BD.get_user_name(str(update.message.from_user.id))}.\n'
            'Доступные Вам функции:\n'
            '/geocoder - Узнать адрес компании\n'
            '/stop используется для остановки любого процесса, в котором Вы находитесь.\n'
            '/reg_company используется для регистрации в какой-либо компании.\n'
            '/edit_post изменить/выбрать роль.\n'
            '/unbinding используется для отключения Вас от вашей компании\n'
            '/all_question при вызове возвращаются все вопросы, реализованные для Вашей '
            'компании.\n '
            'Все остальное бот будет принимать как вопрос, заданный Вами.\n'
            'Приятного использования!')


def add_mailing(update, context):  # добавление рассылки
    update.message.reply_text(
        f'{BD.get_user_name(str(update.message.from_user.id))}, уведомления для пользователей какой компании Вы хотите добавить/удалить?')
    return 1


def what_company(update, context):  # определение компании
    company = update.message.text
    if BD.check_company(company):
        context.user_data['company'] = company
        update.message.reply_text('Какое сообщение хотите, чтоб отправлялось/удалялось?')
        return 2
    else:
        update.message.reply_text('Ошибка: компания с таким названием не найдена.')
        update.message.reply_text('Уведомления для пользователей какой компании Вы хотите добавить/удалить?')
        return 1


def get_text_mailing(update, context):  # редактирование рассылки
    context.user_data['text'] = update.message.text
    update.message.reply_text('''В какую(-ые) даты отправлять или уведомления в какую дату удалить? 
Вводите через запятую с пробелом, в формете день.месяц.год.
Например: 25.05.2022, 23.02.2023''')
    return 3


def all_question(update, context):  # получение всех вопросов
    company = BD.get_user_company(str(update.message.from_user.id))
    a = BD.get_questions(company)
    if a:
        update.message.reply_text('\n'.join([str(x[0] + 1) + '. ' + x[1][0].capitalize() for x in a]))
    else:
        update.message.reply_text(
            f'{BD.get_user_name(str(update.message.from_user.id))}, для Вашей компании не реализованны вопросы.')


def get_date_add(update, context):  # добавление рассылки
    date = update.message.text.split(', ')
    for i in date:
        BD.add_mailing(context.user_data['text'].capitalize(), i, context.user_data['company'].capitalize())
    update.message.reply_text('Успешно! Уведомления ждут своей отправки.')
    return ConversationHandler.END


def stop_new_mailing(update, context):  # завершение
    update.message.reply_text('Добавление уведомления остановлено.')
    return ConversationHandler.END


def get_date_del(update, context):  # удаление рассылки
    date = update.message.text.split(', ')
    for i in date:
        BD.delete_mailing(context.user_data['text'].capitalize(), i, context.user_data['company'].capitalize())
    update.message.reply_text('Успешно! Дата удалена.')
    return ConversationHandler.END


def stop_del_mailing(update, context):  # завершение
    update.message.reply_text('Удаление рассылки остановлено.')
    return ConversationHandler.END


def add_question(update, context):  # редактирование вопроса
    update.message.reply_text(
        f'{BD.get_user_name(str(update.message.from_user.id))}, введите вопрос, который нужно добавить/редактировать/удалить.')
    return 1


def edit_post(update, context):  # редактирование роли
    update.message.reply_text(
        f'{BD.get_user_name(str(update.message.from_user.id))}, введите роль, которую хотите установить. (Клиент, Админ)')
    return 1


def add_answer(update, context):  # редактирование вопроса
    context.user_data['question'] = update.message.text.capitalize()
    update.message.reply_text('Введите ответ на вопрос.')
    return 2


def creating_question(update, context):  # редактирование вопроса
    context.user_data['answer'] = update.message.text.capitalize()
    update.message.reply_text('Введите компанию, участники которой могут задать вопрос.')
    return 3


def stop_question_add(update, context):  # завершение
    update.message.reply_text('Добавление/редактирование/удаление вопроса остановлено.')
    return ConversationHandler.END


def stop_edit_post(update, context):  # завершение
    update.message.reply_text('Редактирование роли остановлено.')
    return ConversationHandler.END


def write_question_add(update, context):  # добавление вопроса
    a = update.message.text.capitalize()
    BD.add_question(context.user_data['question'].capitalize(), context.user_data['answer'].capitalize(), a)

    update.message.reply_text('Вопрос добавлен.')
    return ConversationHandler.END


def write_question_red(update, context):  # редактирование вопроса
    context.user_data['company'] = update.message.text.capitalize()
    if BD.check_question(context.user_data['question'].capitalize(), context.user_data['company']):
        BD.redact_question(context.user_data['question'].capitalize(), context.user_data['answer'].capitalize(),
                           update.message.text.capitalize())
    else:
        update.message.reply_text('Ошибка: данного вопроса у данной компании не существует.')
        update.message.reply_text('Введите вопрос, который нужно добавить/редактировать/удалить.')
        return 1
    update.message.reply_text('Вопрос изменен.')
    return ConversationHandler.END


def write_question_del(update, context):  # удаление вопроса
    context.user_data['company'] = update.message.text.capitalize()
    if BD.check_question_all(context.user_data['question'].capitalize(), context.user_data['answer'].capitalize(),
                             context.user_data['company'].capitalize()):
        BD.delete_question(context.user_data['question'].capitalize(), context.user_data['answer'].capitalize(),
                           context.user_data['company'].capitalize())
    else:
        update.message.reply_text('Ошибка: вопроса с такими характеристиками не существует.')
        update.message.reply_text('Введите вопрос, который нужно добавить/редактировать/удалить.')
        return 1
    update.message.reply_text('Вопрос удален.')
    return ConversationHandler.END


def get_file(update, context):  # получение xlsx файла с информацией из БД
    update.message.reply_text('''Подождите, происходит формирование
таблицы, загрузка и отправление...
Это займет несколько минут. Спасибо за ожидание.''')
    workbook = xlsxwriter.Workbook('Таблица_Excel_БД.xlsx')
    data = BD.get_info_for_file()
    for sheet in data:
        name, stroki = sheet
        worksheet = workbook.add_worksheet(name)
        for row, stroka in enumerate(stroki):
            for i in range(len(stroka)):
                worksheet.write(row, i, stroka[i])
    workbook.close()
    context.bot.sendDocument(chat_id=update.message.from_user.id, document=open('Таблица_Excel_БД.xlsx', mode='rb'))


def send_messange(dp):  # отправление рассылки
    list_of_messanges = BD.get_mailings()
    for mailing in list_of_messanges:
        text, ids = mailing
        for id_ in ids:
            telegram.ext.CallbackContext(dp).bot.sendMessage(chat_id=id_, text=text)


def geocoder(update, context):
    update.message.reply_text('''Узнаю адрес компании...''')
    geocoder_uri = geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": "Нижний Новгород"
    })

    toponym = response.json()["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    delta = "0.045"
    ll = ",".join([toponym_longitude, toponym_lattitude])
    spn = ",".join([delta, delta])

    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="В просторах интернета сказано, что агенство находится в Нижнем Новгороде (точного адреса нет)"
    )


def thr():  # второй поток для рассылки
    while True:
        schedule.run_pending()


def main():  # основной поток, функция
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # schedule.every(7).seconds.do(send_messange, dp)
    schedule.every().day.at("16:30").do(send_messange, dp)  # рассылка уведомлений
    threading.Thread(target=thr).start()
    # сценарии
    script_registration = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, info, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, password_request, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, entering_info, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_reg, pass_user_data=True)],
        allow_reentry=False
    )
    dp.add_handler(script_registration)
    script_linking_company = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('reg_company', linking_company, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, get_name_company_password, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_pass, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_linking, pass_user_data=True)]
    )
    dp.add_handler(script_linking_company)
    dp.add_handler(CommandHandler("unbinding", unbinding_company))
    dp.add_handler(CommandHandler("help", helps))
    dp.add_handler(CommandHandler("geocoder", geocoder))
    dp.add_handler(CommandHandler("get_xlsx_file", get_file))
    reply_keyboard = [['/help', '/stop']]
    global markup
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    dp.add_handler(CommandHandler('all_question', all_question))
    # dp.add_handler(CommandHandler("send_messange", send_messange))
    script_creature_company = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('creating_company', input_name_company, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, input_password_company, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, input_get_telephone, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, creating_company, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_new_company, pass_user_data=True)]
    )
    dp.add_handler(script_creature_company)

    script_del_company = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('delete_company', delete_company, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, delete_comp, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_linking, pass_user_data=True)]
    )
    dp.add_handler(script_del_company)

    script_adding_mailing_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('add_mailing', add_mailing, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, what_company, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_text_mailing, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, get_date_add, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_new_mailing, pass_user_data=True)]
    )
    dp.add_handler(script_adding_mailing_lists)

    script_del_mailing_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('delete_mailing', add_mailing, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, what_company, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_text_mailing, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, get_date_del, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_del_mailing, pass_user_data=True)]
    )
    dp.add_handler(script_del_mailing_lists)

    script_add_question_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('add_question', add_question, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, add_answer, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, creating_question, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, write_question_add, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_question_add, pass_user_data=True)]
    )
    dp.add_handler(script_add_question_lists)

    script_del_question_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('delete_question', add_question, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, add_answer, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, creating_question, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, write_question_del, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_question_add, pass_user_data=True)]
    )
    dp.add_handler(script_del_question_lists)

    script_red_question_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('redact_question', add_question, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, add_answer, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, creating_question, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, write_question_red, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_question_add, pass_user_data=True)]
    )
    dp.add_handler(script_red_question_lists)

    script_edit_user_post = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('edit_post', edit_post, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, edit_post_input_post, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, edit_post_input_password, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_edit_post, pass_user_data=True)]
    )
    dp.add_handler(script_edit_user_post)

    # самый низ
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_question))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()