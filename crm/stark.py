from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from .models import *
from stark.service.stark import site, StarkConfig

from crm.config.Dep import DepConfig
from crm.config.Userinfo import UserConfig
from crm.config.Cour import CourConfig
from crm.config.School import SchoolConfig
from crm.config.class_list import Class_listConfig

site.register(Department, DepConfig)

site.register(UserInfo, UserConfig)

site.register(Course,CourConfig)

site.register(School,SchoolConfig)
site.register(ClassList,Class_listConfig)