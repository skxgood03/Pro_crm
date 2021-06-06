from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from crm.permission.base import RbacPermission
from stark.service.stark import site, StarkConfig,Option


class Class_listConfig(RbacPermission,StarkConfig):

    def display_title(self, row=None, header=False):
        if header:
            return '班级'
        return '%s-%s' % (row.course.name, row.semester)

    def start_date(self, row=None, header=False):
        if header:
            return '开班日期'
        return row.start_date.strftime("%Y-%m-%d")
    list_display = ['id',display_title, 'school',  'price',
                    start_date,
                    # 'graduate_date',
                    'class_teacher',
                    # 'tech_teachers_set__nickname',
                    StarkConfig.display_edit]
    list_filter = [
        Option(field='school',is_choice=False,is_multi=False,text_func=lambda x:x.title,value_func=lambda x:x.pk),
        Option(field='course',is_choice=False,is_multi=False,text_func=lambda x:x.name,value_func=lambda x:x.pk),
    ]