import imp
from django.contrib import admin
from .models import *


admin.site.register(user_type)
admin.site.register(Member)
admin.site.register(Book)
admin.site.register(Borrower)

# Register your models here.
