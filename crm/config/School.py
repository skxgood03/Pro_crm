from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from stark.service.stark import site, StarkConfig
class SchoolConfig(StarkConfig):
    list_display = ['id','title',StarkConfig.display_edit_del]