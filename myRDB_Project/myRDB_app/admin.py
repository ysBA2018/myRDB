from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['identity', 'name', 'first_name', 'deleted', 'orga', 'department', 'group',
                  'zi_organisation',
                  'roles', 'direct_connect_afs', 'direct_connect_gfs', 'direct_connect_tfs', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(AF)
admin.site.register(GF)
admin.site.register(TF)
admin.site.register(Orga)
admin.site.register(Department)
admin.site.register(Group)
admin.site.register(ZI_Organisation)
admin.site.register(TF_Application)


