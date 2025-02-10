from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.AppUser)
admin.site.register(models.Content)
admin.site.register(models.Collect)
admin.site.register(models.Comment)
admin.site.register(models.Message)