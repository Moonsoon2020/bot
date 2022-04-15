import logging
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler
from for_DBwork import DB

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
TOKEN = '5355485794:AAGBNp_ZMuEw8vK1t9UiuuDOV8yOY0OQN_E'
SUPER_PASSWORD = '0000'
BD = DB()


def start(update, context):  # старт
    update.message.reply_text('''Здравствуйте! Я смогу ответить на возникшие у Вас вопросы,
но для начала нужно пройти регистрацию. Напишите, пожалуйста, Вашу роль.
Например: Klient''')
    return 1


def info(update, context):  # функция уточнения положения
    a = update.message.text
    logger.info(' '.join([a, 'Admin', str(a == 'Admin')]))
    if a == 'Admin':
        context.user_data['Post'] = 1
        update.message.reply_text('''Для того чтобы стать администратором,
нужно ввести выданный Вам пароль:
Например: 0000''')
        return 2
    elif a == 'Klient':
        context.user_data['Post'] = 0
        update.message.reply_text('''Готов произвести регистрацию.
Введите Ваше ФИО через пробел.
Например: Иванов Иван Иванович''')
        return 3


def stop_reg(update, context):  # функция внезапной остановки
    update.message.reply_text('Регистрация приостановлена.')
    context.user_data.clear()
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
Например: Klient''')
        return 1


def entering_info(update, context):  # добавление ФИО
    a = update.message.text
    context.user_data['ФИО'] = a
    # добавление пользователя
    fio = context.user_data['ФИО'].split()
    logger.info(str(fio) + str(context.user_data['Post']))
    BD.add_user(fio[0], fio[1], fio[2], context.user_data['Post'], str(update.message.from_user.id))
    if context.user_data['Post'] == 0:
        reg_in_company(update, fio[1])
    context.user_data.clear()
    return ConversationHandler.END


def reg_in_company(update, context):
    update.message.reply_text('''Теперь вы можете вступить в компанию.
Для этого напишите или нажмите на /reg_company''')


def linking_company(update, context):
    logger.info('привязка к компании')
    update.message.reply_text('''Введите название компании, в которую хотите вступить.''')
    return 1


def get_name_company_password(update, context):
    name_company = update.message.text
    context.user_data['NameCompany'] = name_company
    a = BD.check_company(name_company)
    if not a:
        update.message.reply_text('''Произошла ошибка: Компании с таким
названием не существует.
Проверьте введенные данные.''')
        update.message.reply_text('''Введите название компании, в которую хотите вступить.''')
        return 1
    context.user_data['PasswordCompany'] = BD.get_company_password(context.user_data['NameCompany'])
    update.message.reply_text('Компания найдена. Введите пароль.')
    return 2


def get_pass(update, context):
    if context.user_data['PasswordCompany'] != update.message.text:
        update.message.reply_text('Возникла ошибка: введен неверный пароль.')
        update.message.reply_text('Компания найдена. Введите пароль.')
        return 1
    BD.remove_user_company(str(update.message.from_user.id), context.user_data['NameCompany'])
    update.message.reply_text('Вы успешно вступили компанию.')
    return ConversationHandler.END


def stop_linking(update, context):
    update.message.reply_text('''Теперь Вы можете вступить в компанию.
Для этого напишите или нажмите на /reg_company''')
    return ConversationHandler.END


def checking_status(update):
    return False if BD.get_user_post(update.message.from_user.id) == 0 else True


def unbinding_company(update, context):
    BD.remove_user_company(str(update.message.from_user.id), '')
    update.message.reply_text('Вы вышли из компании.')


def get_question(update, context):
    company = BD.get_user_company(str(update.message.from_user.id))
    print(company)
    if company == None:
        if BD.get_user_post(str(update.message.from_user.id)) == 0:
            update.message.reply_text('Вы не можете получить ответ, так как не состоите в компании.')
        else:
            update.message.reply_text('''Вы - администратор! Уверен, ответы на
все интересующие вопросы Вы знаете сами)''')
    else:
        update.message.reply_text(str(BD.get_answer(update.message.text, company)))


def input_name_company(update, context):
    if not checking_status(update):
        update.message.reply_text('Для создания компании вы должны быть администратором.')
        return ConversationHandler.END
    update.message.reply_text('Введите будущее название компании.')
    return 1


def input_password_company(update, context):
    context.user_data['title'] = update.message.text
    update.message.reply_text('Введите пароль компании для входа пользователей.')

    return 2


def input_get_telephone(update, context):
    context.user_data['password'] = update.message.text
    update.message.reply_text('Введите контактный телефон владельца компании (Ваш).')
    return 3


def creating_company(update, context):
    BD.add_company(context.user_data['title'], update.message.text, context.user_data['password'])
    update.message.reply_text('Успешно! Компания создана, а Вы её администратор.')
    context.user_data.clear()
    return ConversationHandler.END


def stop_new_company(update, context):
    update.message.reply_text('Остановка создания компании.')
    return ConversationHandler.END


def delete_company(update, context):
    if not checking_status(update):
        update.message.reply_text('Для создания компании вы должны быть администратором.')
        return
    update.message.reply_text('''Введите название компании, которую 
хотите удалить. ВНИМАНИЕ: это действие отменить будет невозможно.''')
    return 1


def delete_comp(update, context):
    a = update.message.text
    BD.delete_company(a)
    update.message.reply_text('Компания удалена.')


def helps(update, context):
    if checking_status(update):
        update.message.reply_text('Привет, уважаемый пользователь - Admin.\n'
                                  '/stop используется для остановки любого процесса, в котором бы вы не находились.\n '
                                  '/creating_company используется для создания новой компании.\n'
                                  'Данные, используемые при создании компании: название компании, её уникальный '
                                  'пароль, номер телефона.\n '
                                  '/delete_company используется для удаления уже существующей компании. Для удаления '
                                  'необходимо только название.\n '
                                  '/add_mailing используется для создания новой рассылки. Для её создания необходимы \n'
                                  '/delete_mailing используется для удаления рассылки.\n'
                                  '/add_question используется для создания нового вопроса.\n'
                                  '/delete_question используется для удаления вопроса.\n')
    else:
        update.message.reply_text('Привет, уважаемый пользователь.\n'
                                  '/stop используется для остановки любого процесса, в котором вы не находились.\n'
                                  '/reg_company используется для регистрации в какой-либо компании.\n'
                                  '/unbinding используется для отключения вас от вашей компании\n'
                                  '/all_question при вызове возвращаются все вопросы, реализованные для вашей '
                                  'компании.\n '
                                  'Все остальное бот будет принимать как вопрос, заданный вами.')



def add_mailing(update, context):
    update.message.reply_text('Уведомления для пользователей какой компании Вы хотите добавить/удалить?')
    return 1


def what_company(update, context):
    company = update.message.text
    print(company)
    if BD.check_company(company):
        context.user_data['company'] = company
        update.message.reply_text('Какое сообщение хотите, чтоб отправлялось/удалялось?')
        return 2
    else:
        update.message.reply_text('Ошибка: компания с таким названием не найдена.')
        update.message.reply_text('Уведомления для пользователей какой компании Вы хотите добавить/удалить?')
        return 1


def get_text_mailing(update, context):
    context.user_data['text'] = update.message.text
    update.message.reply_text('''В какую(-ые) даты отправлять или уведомления в какую дату удалить? 
Вводите через запятую с пробелом, в формете день.месяц.год.
Например: 25.05.2022, 23.02.2023''')
    return 3


def get_date_add(update, context):
    date = update.message.text.split(', ')
    for i in date:
        BD.add_mailing(context.user_data['text'], i, context.user_data['company'])
    update.message.reply_text('Успешно! Уведомления ждут своей отправки.')
    return ConversationHandler.END


def stop_new_mailing(update, context):
    update.message.reply_text('Добавление функции остановлено.')
    return ConversationHandler.END


def get_date_del(update, context):
    date = update.message.text.split(', ')
    for i in date:
        BD.delete_mailing(context.user_data['text'], i, context.user_data['company'])
    update.message.reply_text('Успешно! Дата удалена.')
    return ConversationHandler.END


def stop_del_mailing(update, context):
    update.message.reply_text('Удаление рассылки остановлено.')
    return ConversationHandler.END


def add_question(update, context):
    update.message.reply_text('Введите вопрос, который нужно добавить/редактировать/удалить.')
    return 1


def add_answer(update, context):
    context.user_data['question'] = update.message.text
    update.message.reply_text('Введите ответ на вопрос.')
    return 2


def creating_question(update, context):
    context.user_data['answer'] = update.message.text
    update.message.reply_text('Введите компанию, участники которой могут задать вопрос.')
    return 3


def stop_question_add(update, context):
    update.message.reply_text('Добавление/реадктирование/удаление вопроса остановлено.')
    return ConversationHandler.END


def write_question_add(update, context):
    a = update.message.text
    print(context.user_data['question'], context.user_data['answer'], a)
    BD.add_question(context.user_data['question'], context.user_data['answer'], a)

    update.message.reply_text('Вопрос добавлен.')
    return ConversationHandler.END


def write_question_red(update, context):
    BD.redact_question(context.user_data['question'], context.user_data['answer'], update.message.text)
    update.message.reply_text('Вопрос изменен.')
    return ConversationHandler.END


def write_question_del(update, context):
    BD.delete_question(context.user_data['question'], context.user_data['answer'], update.message.text)
    update.message.reply_text('Вопрос удален.')
    return ConversationHandler.END


def main():  #
    updater = Updater(TOKEN)
    dp = updater.dispatcher
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
        fallbacks=[CommandHandler('stop', stop_reg, pass_user_data=True)]
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
            3: [[MessageHandler(Filters.text & ~Filters.command, write_question_add, pass_user_data=True)]]
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
            3: [[MessageHandler(Filters.text & ~Filters.command, write_question_del, pass_user_data=True)]]
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
            3: [[MessageHandler(Filters.text & ~Filters.command, write_question_red, pass_user_data=True)]]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_question_add, pass_user_data=True)]
    )
    dp.add_handler(script_red_question_lists)

    # самый низ
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_question))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()