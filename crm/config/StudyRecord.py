from django.conf import settings
from django.db import transaction
from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from django import forms
from stark.service.stark import site, StarkConfig, get_choice_text, Option

class StudyRecordConfig(StarkConfig):
    list_display = ['student',StarkConfig.display_edit]

    def get_queryset(self):
        ccid = self.request.GET.get('ccid')
        if not ccid:
            return StudyRecord.objects.none()
        return StudyRecord.objects.filter(course_record_id=ccid)

    def get_add_btn(self):
        return False