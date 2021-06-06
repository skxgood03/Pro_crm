from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from crm.permission.base import RbacPermission
from stark.service.stark import site, StarkConfig, get_choice_text


class StuConfig(RbacPermission,StarkConfig):

    def display_class_list(self,row=None,header = False):
        if header:
            return '班级'
        class_list = row.class_list.all()
        class_name_list = ["%s%s期" %(row.course.name,row.semester) for row in class_list]
        return ','.join(class_name_list)
    list_display = ['customer','qq','mobile','emergency_contract',
                    get_choice_text('student_status', "学员状态"),
                    'score',
                    display_class_list
                    ]