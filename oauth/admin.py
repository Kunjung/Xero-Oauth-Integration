from django.contrib import admin

# Register your models here.
from oauth.models import Account

admin.site.register(Account)