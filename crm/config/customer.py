from django.conf import settings
from django.db import transaction
from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from django import forms

from crm.permission.base import RbacPermission
from stark.service.stark import site, StarkConfig, get_choice_text, Option


class PubModelForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['consultant', 'status']


class CustConfig(RbacPermission,StarkConfig):
    def display_follow(self, row=None, header=False):
        if header:
            return '记录'
        url = reverse("stark:crm_consultrecord_changelist")
        return mark_safe('<a href = "%s?cid=%s">跟进记录</a>'%(url,row.pk))
    list_display = ['name',
                    'qq',
                    get_choice_text('gender', '性别'),
                    get_choice_text('status', '状态'),
                    display_follow,
                    get_choice_text('source', '来源'),
                    StarkConfig.display_edit_del,
                    ]
    order_by = ['-id']
    search_list = ['name', 'qq']
    list_filter = [
        Option('status', is_choice=True, text_func=lambda x: x[1]),
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
        Option('source', is_choice=True, text_func=lambda x: x[1]),  # ,is_multi=True可多选
    ]


class PublicCustConfig(RbacPermission,StarkConfig):
    list_display = [
        StarkConfig.display_checkbox,
        'name',
        'qq',
        get_choice_text('gender', '性别'),
        get_choice_text('status', '状态'),
        get_choice_text('source', '来源'),
        StarkConfig.display_edit,
        ]

    def multi_apply(self, request):
        """
        申请客户
        :param request:
        :return:
        """
        id_list = request.POST.getlist('pk')
        current_user_id = 3  # 以后要改成session中获取
        my_coustomer_count = Customer.objects.filter(consultant_id=current_user_id, status=2).count()

        if (my_coustomer_count + len(id_list)) > settings.MAX_PRIVATE_CUSTOMER:
            return HttpResponse('用户已达最大限度')
        flag = False
        with transaction.atomic():  # 数据锁
            origin = Customer.objects.filter(id__in=id_list, consultant__isnull=True). \
                select_for_update()
            if len(origin) == len(id_list):
                Customer.objects.filter(id__in=id_list).update(consultant_id=current_user_id)
                flag = True
        if not flag:
            return HttpResponse('已被其他顾问申请请刷新')

    multi_apply.text = '申请客户'
    action_list = [multi_apply]
    order_by = ['-id']
    search_list = ['name', 'qq']
    list_filter = [
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
        Option('source', is_choice=True, text_func=lambda x: x[1]),  # ,is_multi=True可多选
    ]
    model_form_class = PubModelForm

    # 判断公户
    def get_queryset(self):
        return self.model_class.objects.filter(consultant__isnull=True)


class PriModelForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['consultant']


class PrivateCustConfig(RbacPermission,StarkConfig):
    def display_follow(self, row=None, header=False):
        if header:
            return '记录'
        url = reverse("stark:crm_consultrecord_pri_changelist")
        return mark_safe('<a href = "%s?cid=%s">跟进记录</a>'%(url,row.pk))

    list_display = [
        StarkConfig.display_checkbox,
        'name',
        'qq',
        get_choice_text('gender', '性别'),
        get_choice_text('status', '状态'),
        display_follow,
        get_choice_text('source', '来源'),
        StarkConfig.display_edit,
   StarkConfig.display_del ]
    order_by = ['-id']
    search_list = ['name', 'qq']
    list_filter = [
        Option('status', is_choice=True, text_func=lambda x: x[1]),
        Option('gender', is_choice=True, text_func=lambda x: x[1]),
    ]
    model_form_class = PriModelForm

    # 判断私户
    def get_queryset(self):
        current_user_id = 3  # 以后要改成session中获取当前登录用户ID
        return self.model_class.objects.filter(consultant_id=current_user_id)

    def save(self, form, modify=True):
        current_user_id = 3  # 以后要改成session中获取
        form.instance.consultant = UserInfo.objects.get(id=current_user_id)
        return form.save()

    def multi_remove(self, request):
        """
        申请客户
        :param request:
        :return:
        """
        id_list = request.POST.getlist('pk')
        current_user_id = 3  # 以后要改成session中获取
        Customer.objects.filter(consultant_id=current_user_id, status=2, id__in=id_list).update(consultant_id=None)

    multi_remove.text = '移除客户'
    action_list = [multi_remove]
