import logging
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler
from for_DBwork import DB

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
TOKEN = '5342995443:AAEBqyRLrd5AmHEEhCNLyfHVy3td3Qvw-Ec'
SUPER_PASSWORD = '0000'
BD = DB()


def start(update, context):  #
    update.message.reply_text('Старт')
    update.message.reply_text('кто ты')
    return 1


def info(update, context):  # функция уточнения положения
    a = update.message.text
    logger.info(' '.join([a, 'Admin', str(a == 'Admin')]))
    if a == 'Admin':
        context.user_data['Post'] = 1
        update.message.reply_text('пароль')
        return 2
    else:
        context.user_data['Post'] = 0
        update.message.reply_text('ФИО')
        return 3


def stop_reg(update, context):  # функция внезапной остановки
    update.message.reply_text('остановка')
    context.user_data.clear()
    return ConversationHandler.END


def password_request(update, context):  # функция проверки суперпароля, используемого для админов
    a = update.message.text
    logger.info(' '.join([a, SUPER_PASSWORD, str(a == SUPER_PASSWORD)]))
    if a == SUPER_PASSWORD:
        update.message.reply_text('ФИО')
        return 3
    else:
        context.user_data.clear()
        update.message.reply_text('кто ты')
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
    update.message.reply_text('Здравствуйте,  вступиnt в команду. Для этого используйте \\reg_company')


def linking_company(update, context):
    logger.info('fghj')
    update.message.reply_text('команда')
    context.user_data['NameCompany'] = update.message.text
    return 1


def get_name_company_password(update, context):
    a = BD.get_company_password(update.message.text)
    if a is None:
        update.message.reply_text('ещё раз')
        update.message.reply_text('команда')
        return 1
    context.user_data['NameCompany'] = update.message.text
    context.user_data['password'] = a
    return 2


def get_pass(update, context):
    update.message.reply_text('пароль')
    if context.user_data['NameCompany'] != update.message.text:
        update.message.reply_text('ещё раз')
        update.message.reply_text('команда')
        return 1
    BD.remove_user_company(str(update.message.from_user.id), context.user_data['NameCompany'])
    return ConversationHandler.END


def stop_linking(update, context):
    update.message.reply_text('Здравствуйте, в команду. Для этого используйте \\reg_company')
    return ConversationHandler.END


def checking_status(update):
    return False if BD.get_user_post(update.message.from_user.id) == 0 else True


def unbinding_company(update, context):
    BD.remove_user_company(str(update.message.from_user.id), '')


def get_question(update, context):
    company = BD.get_user_company(str(update.message.from_user.id))
    if company in None:
        update.message.reply_text('нет компании')
    else:
        update.message.reply_text(str(BD.get_answer(update.message.text, company)))


def get_name_company(update, context):
    if not checking_status(update):
        update.message.reply_text('у вас нет прав')
        return ConversationHandler.END
    update.message.reply_text('имя')
    return 1


def password_company(update, context):
    context.user_data['title'] = update.message.text
    update.message.reply_text('пароль')

    return 2


def get_telephone(update, context):
    context.user_data['password'] = update.message.text
    update.message.reply_text('телефон')
    return 3


def creating_company(update, context):
    BD.add_company(context.user_data['title'], update.message.text, context.user_data['password'])
    update.message.reply_text('Компания создана')
    return ConversationHandler.END


def stop_new_company(update, context):
    update.message.reply_text('остановка фвв')
    return ConversationHandler.END


def delete_company(update, context):
    update.message.reply_text('введите название')
    BD.delete_company(update.message.text)
    update.message.reply_text('компания удалена')


def helps(update, context):
    if checking_status(update):
        update.message.reply_text('помощь админка')
    else:
        update.message.reply_text('помощь пользователя')


def add_mailing(update, context):
    update.message.reply_text('какая компания')
    return 1


def what_company(update, context):
    if BD.check_company(update.message.text):
        context['company'] = update.message.text
        update.message.reply_text('какая сообщение')
        return 2
    else:
        update.message.reply_text('какая компания')
        return 1


def get_text_mailing(update, context):
    context['text'] = update.message.text
    update.message.reply_text('какая дата')
    return 3


def get_date(update, context):
    date = update.message.text.split(', ')
    for i in date:
        BD.add_mailing(context['text'], i, context['company'])
    update.message.reply_text('ок. всё ок')
    return ConversationHandler.END


def stop_new_mailing(update, context):
    update.message.reply_text('остановка добавления рассылки')
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
    script_creature_company = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('creating_company', get_name_company, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, password_company, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_telephone, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, creating_company, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_new_company, pass_user_data=True)]
    )
    dp.add_handler(script_creature_company)
    dp.add_handler(CommandHandler("delete_company", delete_company))
    dp.add_handler(CommandHandler("help", helps))
    script_adding_mailing_lists = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('add_mailing', add_mailing, pass_user_data=True)],
        # Состояние внутри диалога.
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, what_company, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_text_mailing, pass_user_data=True)],
            3: [MessageHandler(Filters.text & ~Filters.command, get_date, pass_user_data=True)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_new_mailing, pass_user_data=True)]
    )
    dp.add_handler(script_adding_mailing_lists)
    # самый низ
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_question))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
