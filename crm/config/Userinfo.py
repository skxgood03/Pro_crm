from django.urls import path
from django.utils.safestring import mark_safe
from django.shortcuts import *
from crm.models import *
from crm.permission.base import RbacPermission
from stark.service.stark import site, StarkConfig, get_choice_text


class UserConfig(RbacPermission,StarkConfig):
    # 自定义显示性别

    def display_gender(self, row=None, header=False):
        if header:
            return '性别'
        return row.get_gender_display()  # 原始

    # 自定义显示详细信息(扩展)
    def display_detail(self, row=None, header=False):
        if header:
            return '查看详情'
        orl = reverse('stark:crm_userinfo_detail', kwargs={'pk': row.id})
        return mark_safe('<a href = "%s">%s</a>' % (orl, row.names))

    list_display = [
        'id',
        display_detail,

        get_choice_text('gender', "性别"),  # 新用法
        'phone',
        'depart',
        StarkConfig.display_edit_del]

    # 自定义添加详情路由及视图(扩展)
    def extra_url(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name
        urlpatterns = [
            path('detail/<int:pk>', self.wrapper(self.detail_view), name='%s_%s_detail' % info), ]
        return urlpatterns

    def detail_view(self, request, pk):
        return HttpResponse('详情页面；；；')

    # 搜索
    search_list = ['nickname', 'depart__title']
