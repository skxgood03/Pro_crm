from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from stark.service.stark import site, StarkConfig
class CourConfig(StarkConfig):
    list_display = ['id','name',StarkConfig.display_edit_del]