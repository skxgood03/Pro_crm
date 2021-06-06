from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from crm.permission.base import RbacPermission
from stark.service.stark import site, StarkConfig
class DepConfig(RbacPermission,StarkConfig):
    list_display = [StarkConfig.display_checkbox, 'title', StarkConfig.display_edit, StarkConfig.display_del]
    search_list = ['title']