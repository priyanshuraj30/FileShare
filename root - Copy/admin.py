from django.contrib import admin

from .models import Folder
from .models import AllFiles
# Register your models here.

admin.site.register(Folder)

admin.site.register(AllFiles)