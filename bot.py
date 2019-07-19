# -*- coding: utf-8 -*-

import telegram
import threading
import configparser
import requests
import re
import datetime
import time

from crawler import Crawler
from db import Db
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, RegexHandler, Filters

#*************************************
#*************************************
#Necessario alterar o telegramBot token
#Crie seu bot no BootFather
#Altere onde possuir SEU TOKEN AQUI
#*************************************
#*************************************

RELEMBRAR = True

def remember():
    global RELEMBRAR
    while True:
        if datetime.datetime.now().strftime("%H:%M:%S") == "11:00:00":
            if RELEMBRAR:
                RELEMBRAR = False
                database = Db()
                data = datetime.date.today().strftime("%d/%m/%Y")
                livros = database.getLivrosDataAviso(str(data))
                for livro in livros:
                    users = database.getChatID(livro[0])
                    for user in users:
                        chatID = user[0]
                        msg = "Onii-chan, o livro " + str(livro[1]) + " vence em 2 dias." 
                        telegram.Bot('SEU TOKEN AQUI').send_message(chat_id=chatID, text=msg)
        if datetime.datetime.now().strftime("%H:%M:%S") == "10:55:00":
            RELEMBRAR = True

def verificarNumeros(value):
    try:
        int(value)
        return True
    except:
        return False

def cadastrar(bot, update, args):
    chat_id = update.message.chat_id
    dataBase = Db()
    if dataBase.haveSelectUser(chat_id):
        msg = "Parece que você já está cadastrado...\nO Kawaii Koto\nDigite /atualizar [Senha BU] para carregar os livros."
        bot.send_photo(chat_id=chat_id, photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2HmXCboVXGQbtaZ__M4ozhb5fnxxGvYeOmbYyReyxx6Kk4JIZiA')
        bot.send_message(chat_id=chat_id, text=msg)
    else:
        if len(args) == 0:
            msg = "Matte kudasai!\nVocê não digitou sua matricula.\nDigite /cadastrar [Matricula]."
            bot.send_photo(chat_id=chat_id, photo='http://static.tumblr.com/mxarhwc/kjylpbc32/yui_k-on.png.jpg')
            bot.send_message(chat_id=chat_id, text=msg)
        elif len(args[0]) != 8:
            msg = "A matricula precisa ter 8 digitos.\nDigite /cadastrar [Matricula]."
            bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/newsfeed/000/189/032/1319151441001.png')
            bot.send_message(chat_id=chat_id, text=msg)
        elif verificarNumeros(args[0]):
            msg = "O chefe aceitou seu cadastro.\nAgora você é uma garota mágica.\nDigite /atualizar [Senha BU] para carregar os livros."
            bot.send_photo(chat_id=chat_id, photo='https://i.redd.it/06cz9yqe33x01.png')
            bot.send_message(chat_id=chat_id, text=msg)
            dataBase.insertUser(chat_id, args[0])
        else:
            msg = "Barusu, a matricula deve possuir apenas números."
            bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/original/001/147/605/c88.png')
            bot.send_message(chat_id=chat_id, text=msg)

def atualizar(bot, update, args):
    chat_id = update.message.chat_id
    if len(args) == 0:
        msg = "Matte kudasai!\nVocê não digitou sua senha.\nDigite /atualizar [Senha BU]."
        bot.send_photo(chat_id=chat_id, photo='http://static.tumblr.com/mxarhwc/kjylpbc32/yui_k-on.png.jpg')
        bot.send_message(chat_id=chat_id, text=msg)
        return
    elif len(args[0]) < 4 or len(args[0]) > 6:
        msg = "A senha precisa ter de 4 a 6 digitos.\nDigite /atualizar [Senha BU]."
        bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/newsfeed/000/189/032/1319151441001.png')
        bot.send_message(chat_id=chat_id, text=msg)
        return
    elif not verificarNumeros(args[0]):
        msg = "Subaru-kun, a senha deve possuir apenas números."
        bot.send_photo(chat_id=chat_id, photo='https://img.fireden.net/v/image/1484/98/1484987967315.jpg')
        bot.send_message(chat_id=chat_id, text=msg)
        return

    dataBase = Db()
    if dataBase.haveSelectUser(chat_id):
        matricula = dataBase.getMatricula(chat_id)
        crawler = Crawler()
        if crawler.crawler(matricula, args[0]):
            msg = "Atualizado!"
            main_menu_keyboard = [[telegram.KeyboardButton('/livros')]]
            reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
            bot.send_photo(chat_id=chat_id, photo='http://orig02.deviantart.net/cfa7/f/2012/259/9/e/mami_tomoe_render_by_moeblueberry1771-d5evnl7.png')
            bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_kb_markup)
        else:
            msg = "What isn't remembered never happened.\nMemory is merely a record.\nYou just need to re-write that record.\Matricula ou senha inválida"
            bot.send_photo(chat_id=chat_id, photo='https://wired-7.org/lain/src/1558910195719.jpg')
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        msg = "Is this a usuário não cadastrado?\nDigite /cadastrar [Matricula]."
        bot.send_photo(chat_id=chat_id, photo='https://assets3.thrillist.com/v1/image/2762016/size/tmg-article_default_mobile.jpg')
        bot.send_message(chat_id=chat_id, text=msg)

def livros(bot, update):
    chat_id = update.message.chat_id
    dataBase = Db()
    if dataBase.haveSelectUser(chat_id):
        matricula = dataBase.getMatricula(chat_id)
        livros = dataBase.getLivros(matricula)
        if len(livros) == 0:
            msg = "Não encontramos seus livros, mas achamos uma cabeça, serve?\nSe já pegou algum livro digite /atualizar [Senha BU]."
            bot.send_photo(chat_id=chat_id, photo='https://pm1.narvii.com/5745/9ec9ee24f7e95aacff2f31f32b2c00051d61d732_hq.jpg')
            bot.send_message(chat_id=chat_id, text=msg)
        else:
            msg = "Aqui estão os livros que você pegou na BU.\nSe não estiverem todos, digite /atualizar [Senha BU]."
            bot.send_photo(chat_id=chat_id, photo='https://media.mstdn.io/mstdn-media/media_attachments/files/001/331/809/small/e9ee4fed3e731726.png')
            bot.send_message(chat_id=chat_id, text=msg)
            for livro in livros:
                msg = str(livro[0])+"\nData de Devolução: "+str(livro[1])+"\nRenovações: "+str(livro[2])
                bot.send_message(chat_id=chat_id, text=msg)
    else:
        msg = "Is this a usuário não cadastrado?\nDigite /cadastrar [Matricula]."
        bot.send_photo(chat_id=chat_id, photo='https://assets3.thrillist.com/v1/image/2762016/size/tmg-article_default_mobile.jpg')
        bot.send_message(chat_id=chat_id, text=msg)

def alterar(bot, update, args):
    chat_id = update.message.chat_id
    dataBase = Db()
    if dataBase.haveSelectUser(chat_id):
        if len(args) == 0:
            msg = "Matte kudasai!\nVocê não digitou sua matricula.\nDigite /alterar [Matricula]."
            bot.send_photo(chat_id=chat_id, photo='http://static.tumblr.com/mxarhwc/kjylpbc32/yui_k-on.png.jpg')
            bot.send_message(chat_id=chat_id, text=msg)
        elif len(args[0]) != 8:
            msg = "A matricula precisa ter 8 digitos.\nDigite /alterar [Matricula]."
            bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/newsfeed/000/189/032/1319151441001.png')
            bot.send_message(chat_id=chat_id, text=msg)
        elif verificarNumeros(args[0]):
            msg = "O chefe aceitou a alteração.\nVocê ainda é uma garota mágica.\nDigite /atualizar [Senha BU] para carregar os livros."
            bot.send_photo(chat_id=chat_id, photo='https://i.redd.it/06cz9yqe33x01.png')
            bot.send_message(chat_id=chat_id, text=msg)
            dataBase.updateMatricula(args[0], chat_id)
        else:
            msg = "Barusu, a matricula deve possuir apenas números."
            bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/original/001/147/605/c88.png')
            bot.send_message(chat_id=chat_id, text=msg)
    else:
        msg = "Você ainda não se cadastrou.\nDigite /cadastrar [Matricula]."
        bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/original/001/147/605/c88.png')
        bot.send_message(chat_id=chat_id, text=msg)

def help(bot, update):
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo='https://i.kym-cdn.com/photos/images/original/001/261/628/47b.jpg')
    bot.send_message(chat_id=chat_id, text="Está tão perdido quanto a Akko?")
    bot.send_message(chat_id=chat_id, text="/cadastrar [Numero da matricula]\n->Para se cadastrar")
    bot.send_message(chat_id=chat_id, text="/alterar [Numero da matricula]\n->Para alterar o número da matricula")
    bot.send_message(chat_id=chat_id, text="/atualizar [Senha BU]\n->Para atualizar os livros")
    bot.send_message(chat_id=chat_id, text="/livros\n->Para mostrar os livros")
    bot.send_message(chat_id=chat_id, text="/avisar\n->Informações sobre os avisos")
    bot.send_message(chat_id=chat_id, text="/info\n->Informações sobre o criador")

def avisar(bot, update):
    chat_id = update.message.chat_id
    msg = "Você (talvez) receberá uma mensagem 2 dias antes do seu livro vencer, às 11hrs. Nunca se sabe o dia de amanhã, pode ser que eu esteja desativado."
    bot.send_message(chat_id=chat_id, text=msg)

def info(bot, update):
    chat_id = update.message.chat_id
    msg = "Esse bot foi criado aleatoriamente por alguém vulgarmente chamado de Josefo depois desse lindo rapaz ter ganhado 1 real de multa na BU por atrasar a devolução por exatamente 1 dia."
    bot.send_message(chat_id=chat_id, text=msg)

def start(bot, update):
    chat_id = update.message.chat_id
    msg = "Alguém chamou a detetive Chika para descobrir quando os livros da BU precisam ser devolvidos?"
    main_menu_keyboard = [[telegram.KeyboardButton('/livros')], [telegram.KeyboardButton('/help')]]
    reply_kb_markup = telegram.ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True, one_time_keyboard=True)
    bot.send_photo(chat_id=chat_id, photo='https://www.geekgirlauthority.com/wp-content/uploads/2019/02/kaguyasama-detective-chika-2-627x376.png')
    bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_kb_markup)

def main():
    #Bot
    updater = Updater('SEU TOKEN AQUI')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('livros',livros))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('avisar',avisar))
    dp.add_handler(CommandHandler('info',info))
    dp.add_handler(CommandHandler('alterar',alterar, pass_args=True))
    dp.add_handler(CommandHandler('atualizar',atualizar, pass_args=True))
    dp.add_handler(CommandHandler('cadastrar',cadastrar, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, start))
    rememberThread = threading.Thread(target = remember)
    rememberThread.start()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    #Configurações iniciais
    dataBase = Db()
    dataBase.create_tables()
    main()