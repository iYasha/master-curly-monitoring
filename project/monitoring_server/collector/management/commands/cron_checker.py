"""
Server shutdown checker by cron expression
"""

from django.core.management.base import BaseCommand
from monitoring_server.collector.models import *
import croniter
from datetime import datetime, timedelta
import telebot


def get_next_cron(cron_expression: str, last_request: datetime):
    cron = croniter.croniter(cron_expression, last_request)
    return cron.get_next(datetime)


class Command(BaseCommand):
    help = 'Проверяет не упал ли сервер, сервер считается отключенным, когда он не отправляет запросы в течении ' \
           'указаного времени по крону '

    def handle(self, *args, **options):
        now = datetime.now()
        servers = Server.objects.all()
        for server in servers:
            last_request = ServerRequest.objects.filter(server=server).order_by('-created_at')[:1]
            if len(last_request) == 0:
                continue
            last_request = last_request[0]
            next_cron = get_next_cron(server.cron_expression, last_request.created_at).strftime('%Y-%m-%d %H:%M')
            next_cron += timedelta(minutes=2)
            next_cron = datetime.strptime(next_cron, '%Y-%m-%d %H:%M')
            if next_cron < now and (server.token is not None and server.chat_ids is not None):
                bot = telebot.TeleBot(server.token)
                delta_time = (now - next_cron)
                minute = round(delta_time.seconds / 60)
                Notification(server=server, reason='SD').save()
                delta_time = f'{delta_time.days} дней {minute} минут'
                for chat_id in server.chat_ids:
                    bot.send_message(
                        chat_id=chat_id[0],
                        text=f'📶 <b>Статус</b>: Важно\n\n'
                             f'💻 <b>Сервер</b>: {server.name}\n\n'
                             f'🆔 <b>IP</b>: {server.ip}\n\n'
                             f'📭 <b>Тип уведомления</b>: Сервер не отвечает\n\n'
                             f'📝 <b>Причина</b>: Нет данных от сервера уже {delta_time}',
                        parse_mode='html'
                    )
