from django.contrib import admin

from mongodata.models import Data, SensitiveData

# Register your models here.

admin.site.register(Data)
admin.site.register(SensitiveData)
