from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'username',
        'date_joined',
        'last_login',
        'is_staff',
    )

    # as we are using custom model,
    # we need the below code to modify the view
    filter_horizontal = ()
    list_filter = ()

    # we want to click on first_name and last_name to open the object
    list_display_links = ('email', 'first_name', 'last_name')

    # making date fields as readonly
    readonly_fields = ('date_joined', 'last_login')

    # sort the display list by date_joined in descending order
    ordering = ('-date_joined',)

    # making password as non-editable
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
