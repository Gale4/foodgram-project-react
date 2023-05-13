from django.contrib import admin

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_staff')
    list_filter = ('email', 'username')


class SubscribeAdmin(admin.ModelAdmin):
    list_filter = ('subscriber', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
