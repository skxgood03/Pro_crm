from django.conf import settings
from django.db import transaction
from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from django import forms
from stark.service.stark import site, StarkConfig, get_choice_text, Option


class CourseRecordConfig(StarkConfig):
    def display_title(self, row=None, header=False):
        if header:
            return "上课记录"
        tpl = "%s s%sday%s" %(row.class_object.course.name,row.class_object.semester,row.day_num)
        return tpl

    def display_study_title(self, row=None, header=False):
        if header:
            return "学习记录"
        url = reverse('stark:crm_studyrecord_changelist')
        return mark_safe('<a href= "%s?ccid=%s">学习记录</a>'%(url,row.pk))

    list_display = [StarkConfig.display_checkbox,display_title,display_study_title,StarkConfig.display_edit_del]

    def multi_init(self, request):
        """
        批量初始化
        :param request:
        :return:
        找到选中上课记录的班级
        找到班级下的所有人
        为每个人生成一条学习记录
        """
        id_list = request.POST.getlist('pk')
        for nid in id_list:
            record_obj = CourseRecord.objects.get(id=nid)
            stu_list = Student.objects.filter(class_list=record_obj.class_object)
            exists = StudyRecord.objects.filter(course_record=record_obj).exists() #判断是否有当天记录
            if exists:
                continue
            study_record_list = []
            for stu in stu_list:
                study_record_list.append(StudyRecord(course_record=record_obj,student=stu))
            StudyRecord.objects.bulk_create(study_record_list) #批量增加

    multi_init.text = '批量初始化'
    action_list = [multi_init]