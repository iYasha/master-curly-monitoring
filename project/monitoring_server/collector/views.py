from django.http import HttpResponse, HttpRequest
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
import telebot
from monitoring_server.collector.utilities import *


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def stats(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(json.loads(request.body))
        ip = get_client_ip(request)
        try:
            server = Server.objects.get(ip=ip)
        except Server.DoesNotExist:
            server = Server(ip=ip, name=ip)
            server.save()
        ServerRequest(server=server).save()
        percent_usage = UsageCPU(server=server, **data['cpu']['percent_usage'])
        percent_usage.save()
        sensors = TempCPU(server=server, **data['cpu']['sensors_temperatures'])
        sensors.save()
        cpu = CPU(server=server, count=data['cpu']['count'], percent_usage=percent_usage, sensors_temperatures=sensors)
        cpu.save()
        ram = RAM(server=server, **data['ram'])
        ram.save()
        disk = DiskUsage(server=server, **data['disk'])
        disk.save()
        for docker_data in data['docker']:
            state = DockerState(server=server, **docker_data['state'])
            state.save()
            docker = Docker(
                server=server,
                state=state,
                restart_count=docker_data['restart_count'],
                name=docker_data['name']
            )
            docker.save()
        message = None
        disk_percentage = round((disk.used / disk.total) * 100, 2)
        ram_percentage = round((ram.used / ram.total) * 100, 2)
        if disk_percentage > 90:
            message = f'📶 <b>Статус</b>: Важно\n\n' \
                      f'💻 <b>Сервер</b>: {server.name}\n\n' \
                      f'🆔 <b>IP</b>: {server.ip}\n\n' \
                      f'📭 <b>Тип уведомления</b>: Заканчивается место на диске\n\n' \
                      f'📝 <b>Причина</b>: На сервере занято более <b>{disk_percentage}%</b> диска. Доступно: <code>{disk.free} gb</code>'
        if ram_percentage > 90:
            message = f'📶 <b>Статус</b>: Важно\n\n' \
                      f'💻 <b>Сервер</b>: {server.name}\n\n' \
                      f'🆔 <b>IP</b>: {server.ip}\n\n' \
                      f'📭 <b>Тип уведомления</b>: Заканчивается ОЗУ на сервере\n\n' \
                      f'📝 <b>Причина</b>: На сервере занято более <b>{ram_percentage}%</b> ОЗУ. Доступно: <code>{ram.free} gb</code>'
        if all([server.token, server.chat_ids, message]):
            bot = telebot.TeleBot(server.token)
            for chat_id in server.chat_ids:
                bot.send_message(
                    chat_id=chat_id[0],
                    text=message,
                    parse_mode='html'
                )
        return HttpResponse(json.dumps({
            'success': True
        }))
    return HttpResponse(json.dumps({
        'success': False
    }), 404)


@csrf_exempt
def logs(request: HttpRequest):
    if request.method == 'POST':
        data = json.loads(json.loads(request.body))
        ip = get_client_ip(request)
        try:
            server = Server.objects.get(ip=ip)
        except Server.DoesNotExist:
            server = Server(ip=ip, name=ip)
            server.save()
        ServerRequest(server=server).save()
        logs = ServerLogs(server=server, **data)
        logs.save()
        notification_type = None
        if not 200 <= int(logs.status_code) <= 299:
            notification_type = 'Ответ от сервера не успешный'
            # Notification(reason='ST', server=server).save()
        if logs.duration > 20:
            notification_type = 'Ответ от сервера слишком долгий'
            # Notification(reason='SH', server=server).save()
        if all([notification_type, server.token, server.chat_ids]):
            bot = telebot.TeleBot(server.token)
            request_body = pretty_json(logs.request_body).strip()
            request_body = 'Нет' if len(request_body) == 0 else request_body
            for chat_id in server.chat_ids:
                bot.send_message(
                    chat_id=chat_id[0],
                    text=f'📶 *Статус*: Информация\n\n'
                         f'💻 *Сервер*: {server.name}\n\n'
                         f'🆔 *IP*: {server.ip}\n\n'
                         f'📭 *Тип уведомления*: {notification_type}\n\n'
                         f'🔑 *Ссылка*: {logs.url}\n\n'
                         f'🚪 *Endpoint*: {logs.endpoint}\n\n'
                         f'⏳ *Время ответа*: {logs.duration}s\n\n'
                         f'🕒 *Время отправки запроса*: {logs.created_at.strftime("%d-%m-%Y %H:%M")}\n\n'
                         f'📦 *Тело запроса*: \n`{request_body}`\n\n'
                         f'📧 *Ответ*: \n`{pretty_json(logs.response_body)}`\n\n'
                         f'🧾 *Код ответа*: {logs.status_code}\n\n',
                    parse_mode='markdown'
                )
        return HttpResponse(json.dumps({
            'success': True
        }))
    return HttpResponse(json.dumps({
        'success': False
    }), 404)
