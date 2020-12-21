from django.db import models
from django.contrib.postgres.fields import ArrayField


class Server(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=255)
    cron_expression = models.CharField(max_length=255, help_text='cron expression', null=True, blank=True)
    name = models.CharField(max_length=255)
    chat_ids = ArrayField(
        ArrayField(models.CharField(max_length=255)), blank=True, null=True
    )
    token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class NotificationDuration(models.Model):
    NOTIFICATION_TYPES = [
        ('UK', 'unknown'),
        ('SD', 'server_down'),
        ('SH', 'server_high_timeout'),
        ('ST', 'status_code_not_success'),
        ('LD', 'low_disk_space'),
        ('LR', 'low_ram'),
        ('LC', 'low_cpu'),
        ('DS', 'container_stopped'),
        ('DR', 'container_restarting'),
        ('DH', 'container_high_restarting'),
    ]

    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    duration = models.IntegerField()
    reason = models.CharField(max_length=255, choices=NOTIFICATION_TYPES, default='UK')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server} | {self.reason}'


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('UK', 'unknown'),
        ('SD', 'server_down'),
        ('SH', 'server_high_timeout'),
        ('ST', 'status_code_not_success'),
        ('LD', 'low_disk_space'),
        ('LR', 'low_ram'),
        ('LC', 'low_cpu'),
        ('DS', 'container_stopped'),
        ('DR', 'container_restarting'),
        ('DH', 'container_high_restarting'),
    ]

    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, choices=NOTIFICATION_TYPES, default='UK')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server} | {self.reason}'


class ServerRequest(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class DiskUsage(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    total = models.FloatField()
    used = models.FloatField()
    free = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class RAM(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    total = models.FloatField()
    used = models.FloatField()
    free = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class UsageCPU(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    last_minute = models.FloatField()
    last_five_minute = models.FloatField()
    last_fifteen_minute = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class TempCPU(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    current = models.FloatField()
    high = models.FloatField()
    critical = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class CPU(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    count = models.IntegerField()
    percent_usage = models.ForeignKey(UsageCPU, on_delete=models.SET_NULL, null=True, blank=True)
    sensors_temperatures = models.ForeignKey(TempCPU, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class DockerState(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    running = models.BooleanField()
    paused = models.BooleanField()
    restarting = models.BooleanField()
    dead = models.BooleanField()
    pid = models.IntegerField()
    exit_code = models.IntegerField()
    error = models.TextField()
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class Docker(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    state = models.ForeignKey(DockerState, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    restart_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | id: {self.id}'


class ServerLogs(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    url = models.TextField()
    duration = models.FloatField()
    ip = models.CharField(max_length=255)
    request_body = models.TextField()
    headers = models.TextField()
    status_code = models.IntegerField()
    response_body = models.TextField()
    endpoint = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.server.name} | {self.endpoint} | {self.status_code}'
