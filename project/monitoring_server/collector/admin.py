from django.contrib import admin
from .models import *

admin.site.register(Server)
admin.site.register(ServerRequest)
admin.site.register(DiskUsage)
admin.site.register(RAM)
admin.site.register(UsageCPU)
admin.site.register(TempCPU)
admin.site.register(CPU)
admin.site.register(DockerState)
admin.site.register(Docker)
admin.site.register(ServerLogs)
admin.site.register(Notification)
admin.site.register(NotificationDuration)
