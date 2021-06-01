from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from stark.service.stark import site, StarkConfig
class DepConfig(StarkConfig):
    list_display = [StarkConfig.display_checkbox, 'title', StarkConfig.display_edit, StarkConfig.display_del]
    search_list = ['title']