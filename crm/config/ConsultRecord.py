from django.conf import settings
from django.db import transaction
from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from django import forms
from stark.service.stark import site, StarkConfig, get_choice_text, Option

class ConsultConfig(StarkConfig):
    list_display = ['customer','note','consultant']

    def get_queryset(self):
        cid = self.request.GET.get('cid')
        if cid:
            return ConsultRecord.objects.filter(customer_id=cid)
        return ConsultRecord.objects

class PriModelForm(forms.ModelForm):
    class Meta:
        model = ConsultRecord
        exclude = ['customer','consultant']

class PirConsultConfig(StarkConfig):
    list_display = ['customer','note','consultant',StarkConfig.display_edit_del]
    model_form_class = PriModelForm
    def get_queryset(self):
        cid = self.request.GET.get('cid')
        current_user_id = 3  # 以后要改成session中获取
        if cid:
            return ConsultRecord.objects.filter(customer_id=cid,customer__consultant_id = current_user_id)
        return ConsultRecord.objects.filter(customer__consultant_id = current_user_id)


    def save(self,form,modify=False):
        if not modify:
            params = self.request.GET.get('_filter')
            cid,num = params.split('=',maxsplit=1)
            form.instance.customer = Customer.objects.get(id=num)

            current_user_id = 3  # 以后要改成session中获取
            form.instance.consultant = UserInfo.objects.get(id=current_user_id)
        form.save()