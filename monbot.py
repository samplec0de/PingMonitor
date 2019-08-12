import os
import time

import telebot
import logging
import subprocess
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

bot = telebot.TeleBot(open('token.txt', 'r').read())
# <Fill here>
admin_ids = []
hosts = []
# </Fill here>
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt="[%d.%m.%Y] %H:%M")
executor = ThreadPoolExecutor()
os.remove('status')
if not os.path.isfile('status'):
    f = open('status', 'w')
    f.write(str(dict.fromkeys(hosts, True)))
    f.close()


def ping(ip):
    ping_command = ['ping', ip, '-c 1']
    shell_needed = False
    ping_output = subprocess.run(ping_command, shell=shell_needed, stdout=subprocess.PIPE)
    success = ping_output.returncode
    return True if success == 0 else False


def send(msg):
    for user_id in admin_ids:
        try:
            bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
        except:
            pass
            # traceback.print_exc(file='error.log')


def ping_task():
    global hosts
    while True:
        try:
            last_online = eval(open('status', 'r').read())
            print(last_online)
            for host in hosts:
                if ping(host):
                    online = True
                else:
                    online = False
                logging.info(f"{host} is {online}")
                if online:
                    if not last_online[host]:
                        send(f"<i>{host}</i>: <b>OK</b>")
                        last_online[host] = True
                else:
                    if last_online[host]:
                        send(f"<i>{host}</i>: <b>BAD</b>")
                        last_online[host] = False
                        print(last_online[host])
            f = open('status', 'w')
            f.write(str(last_online))
            f.close()
            logging.info(str(last_online))
        except:
            traceback.print_exc(file=open('error.log', 'a'))


@bot.message_handler(commands=['status'])
def status(message):
    last_online = eval(open('status', 'r').read())
    if message.chat.id not in admin_ids:
        logging.info(u"Пользователю %s запрещён доступ к команде, так как у него нет прав администратора."
                     % message.chat.username)
        return
    ans = ""
    for host in last_online:
        ans += f"<i>{host}</i>: <b>{'OK' if last_online[host] else 'BAD'}</b>\n"
    # print(ans)
    bot.send_message(chat_id=message.chat.id, text=ans, parse_mode="HTML")


print('YES')
executor.submit(ping_task)
while True:
    try:
        bot.polling()
    except:
        traceback.print_exc(file=open('error.log', 'a'))
