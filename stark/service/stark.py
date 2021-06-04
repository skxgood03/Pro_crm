from django.shortcuts import *
from django.urls import path
from types import FunctionType
import functools
from django import forms
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.db.models.fields.related import ForeignKey,ManyToManyField
from django.http import QueryDict

class ModelConfigMapping(object):
    def __init__(self,model,config,prev):
        self.model = model
        self.config = config
        self.prev = prev

def get_choice_text(field,head):
    """
    #使用闭包
    公共组件获取choice对应的内容
    :param field: 字段名称
    :param head: 名称
    :return:
    """

    def inner(self, row=None, header=False):
        if header:
            return head
        func_name = 'get_%s_display'%field
        return getattr(row,func_name)() #get_field_display()

    return inner

class Row(object):
    def __init__(self,data_list,option,query_dict):
        """
        元组
        :param data_list: 元组或queryset
        """
        self.data_list = data_list
        self.option = option
        self.query_dict =query_dict

    def __iter__(self):
        yield '<div class="whole">'
        tatal_query_dict = self.query_dict.copy()
        tatal_query_dict._mutable = True
        origin_value_list = self.query_dict.getlist(self.option.field) #获取到选中的
        if origin_value_list:
            tatal_query_dict.pop(self.option.field)
            yield '<a href="?%s">全部</a>'%(tatal_query_dict.urlencode(),)
        else:
            yield '<a class ="active" style="margin-top: -5px;" href="?%s">全部</a>'%(tatal_query_dict.urlencode(),)

        yield ' </div>'
        yield '<div class="others">'
        for item in self.data_list:
            val = self.option.get_value(item)
            text = self.option.get_text(item)
            query_dict = self.query_dict.copy()
            query_dict._mutable = True
            if not self.option.is_multi: #单选
                if  str(val) in origin_value_list:
                    query_dict.pop(self.option.field)
                    yield '<a class ="active" href="?%s">%s</a>' % (query_dict.urlencode(), self.option.get_text(item))
                else:
                    query_dict[self.option.field] = val
                    yield '<a href="?%s">%s</a>'% (query_dict.urlencode(),self.option.get_text(item))
            else: #多选
                multi_val_list = query_dict.getlist(self.option.field)
                if str(val) in origin_value_list:
                    #已经选项的，把自己去掉
                    multi_val_list.remove(str(val))
                    query_dict.setlist(self.option.field,multi_val_list)
                    yield '<a class ="active" href="?%s">%s</a>' % (query_dict.urlencode(), self.option.get_text(item))
                else:
                    multi_val_list.append(val)
                    query_dict.setlist(self.option.field,multi_val_list)
                    yield '<a href="?%s">%s</a>'% (query_dict.urlencode(),self.option.get_text(item))
        yield ' </div>'


class Option(object):
    def __init__(self, field, condittion=None, is_choice=False,text_func=None,value_func=None,is_multi=False):

        self.field = field
        self.is_choice = is_choice
        if not condittion:
            condittion = {}
        self.condittion = condittion
        self.text_func = text_func
        self.value_func = value_func
        self.is_multi = is_multi

    def get_queryset(self, _field, model_class,query_dict):
        if isinstance(_field, ForeignKey) or isinstance(_field, ManyToManyField) :
            row = Row(_field.remote_field.model.objects.filter(**self.condittion),self,query_dict)

        else:
            if self.is_choice:
                row = Row(_field.choices,self,query_dict)
            else:
                row = Row(model_class.objects.filter(**self.condittion),self,query_dict)
        return row
    def get_text(self,item):
        if self.text_func:
            return self.text_func(item)
        return str(item)

    def get_value(self,item):
        if self.value_func:
            return self.value_func(item)
        if self.is_choice:
            return item[0]
        return item.pk
        


class ChangeList(object):
    """
    封装列表页面需要的所有功能
    """

    def __init__(self, config, queryset, q, search_list, page):
        self.q = q
        self.search_list = search_list
        self.page = page
        self.config = config
        ##########action操作##########
        self.action_list = [{'name': func.__name__, 'text': func.text} for func in config.get_action_list()]
        ##########添加按钮############
        self.add_btn = config.get_add_btn()
        self.queryset = queryset
        self.list_display = config.get_list_display()
        self.list_filter = config.get_list_filter()
    def get_list_filter_rows(self):
        for option in self.list_filter:
            # 如果 field = ‘name’ -> 查Depact所有数据
            # 如果 field = ‘user’ -> 查Userinfo所有数据
            _field = self.config.model_class._meta.get_field(option.field)  # 获取类型
            # print(_field)
            yield  option.get_queryset(_field, self.config.model_class,self.config.request.GET)


class StarkConfig(object):
    def display_checkbox(self, row=None, header=False):
        if header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="{}"/>'.format(row.pk))

    def display_edit(self, row=None, header=False):
        if header:
            return '编辑'
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.size.namespace
        name = '%s:%s_%s_change' % (namespace, app_label, model_name)
        edit_url = reverse(name, kwargs={'pk': row.pk})
        return mark_safe(
            '<a href = "%s"><i class="fa fa-edit" aria-hidden="true"></i></a>' % self.reverse_edit_url(row))

    def display_del(self, row=None, header=False):
        if header:
            return '删除'

        return mark_safe('<a href = "%s"><i class="fa fa-trash-o"></i></a>' % self.reverse_del_url(row))

    def display_edit_del(self, row=None, header=False):
        if header:
            return '操作'
        tpl = """
        <a href='%s'><i class="fa fa-edit" aria-hidden="true"></i></a> | 
        <a href='%s'><i class="fa fa-trash-o"></i></a>
        """ % (self.reverse_edit_url(row), self.reverse_del_url(row))
        return mark_safe(tpl)

    def multi_delete(self, request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()
        # return HttpResponse('删除成功')

    multi_delete.text = '批量删除'

    def multi_init(sel, request):
        print('批量初始化')

    multi_init.text = '批量初始化'

    order_by = []
    list_display = []
    model_form_class = None
    action_list = []
    search_list = []
    list_filter = []

    def __init__(self, model_class, size,prev):
        self.model_class = model_class
        self.size = size
        self.prev = prev
        self.request = None

        self.back_condition_key = '_filter'

    def get_order_by(self):
        return self.order_by

    def get_list_display(self):
        return self.list_display

    def get_add_btn(self):
        return mark_safe('<a href="%s" class= "btn btn-success">添加</a>' % self.reverse_add_url())

    def get_model_form_class(self):
        """获取modelform类"""
        if self.model_form_class:
            return self.model_form_class

        class AddModelForm(forms.ModelForm):
            class Meta:
                model = self.model_class
                fields = '__all__'

        return AddModelForm

    def get_action_list(self):
        val = []
        val.extend(self.action_list)
        return val

    def get_action_dict(self):
        val = {}
        for item in self.action_list:
            val[item.__name__] = item
        return val

    def get_search_list(self):
        val = []
        val.extend(self.search_list)
        return val

    def get_search_condition(self, request):

        search_list = self.get_search_list()
        q = request.GET.get('q', '')
        con = Q()
        con.connector = 'OR'
        if q:
            for field in search_list:
                con.children.append(('%s__contains' % field, q))
        return search_list, q, con

    def get_list_filter(self):
        val = []
        val.extend(self.list_filter)
        return val

    def get_list_filter_condition(self):
        # 获取组合搜索筛选

        comb_condition= {}
        for option in self.get_list_filter():
            element = self.request.GET.getlist(option.field)
            if element:
                comb_condition['%s__in'%option.field] = element
        return comb_condition

    def get_queryset(self):
        return self.model_class.objects
    def changelist_view(self, request):
        """
        列表页面
        :param request:
        :return:
        """
        if request.method == "POST":
            action_name = request.POST.get('action')
            action_dict = self.get_action_dict()
            if action_name not in action_dict:
                return HttpResponse('请求非法')
            response = getattr(self, action_name)(request)
            if response:
                return response
        ########## 处理搜索##########
        search_list, q, con = self.get_search_condition(request)

        ########## 处理分页 ##########
        from stark.utils.pagination import Pagination
        base_url = request.path_info
        query_params = request.GET.copy()
        query_params._mutable = True
        all_count = self.model_class.objects.filter(con).count()
        page = Pagination(request.GET.get('page'), all_count, base_url, query_params)

       #获取组合搜索筛选
        list_filter = self.get_list_filter()
        origin_queryset = self.get_queryset()
        queryset = origin_queryset.filter(con).filter(**self.get_list_filter_condition()).order_by(*self.get_order_by()).distinct()[page.start:page.end]

        cl = ChangeList(self, queryset, q, search_list, page)

        #########组合搜索##########
        # list_filter = ['name','user']
        list_filter = self.get_list_filter()
        # print(list_filter)


            # print(list_filter_rows)
        #########处理表格##########
        # inclusion_tag
        # 生成器

        return render(request, 'stark/changelist.html', {'cl': cl})

    def save(self,form,modify=False):
        """
        :param form:
        :param modify:True 表示要修改，False新增
        :return:
        """
        return form.save()
    def add_view(self, request):
        """
        添加页面
        :param request:
        :return:
        """
        AddModelForm = self.get_model_form_class()
        if request.method == 'GET':
            form = AddModelForm()
            return render(request, 'stark/change.html', {'form': form})
        form = AddModelForm(request.POST)
        if form.is_valid():
            self.save(form,modify=False)
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def change_view(self, request, pk):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse('数据不存在')
        ModelFromClass = self.get_model_form_class()
        if request.method == "GET":
            form = ModelFromClass(instance=obj)
            return render(request, 'stark/change.html', {'form': form})
        form = ModelFromClass(data=request.POST, instance=obj)
        if form.is_valid():
            self.save(form,modify=True)
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def delete_view(self, request, pk):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """
        obj = self.model_class.objects.filter(pk=pk).delete()

        return redirect(self.reverse_list_url())

    def wrapper(self, func):
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        urlpatterns = [
            path('list/', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            path('add/', self.wrapper(self.add_view), name=self.get_add_url_name),
            path('change/<int:pk>/', self.wrapper(self.change_view), name=self.get_change_url_name),
            path('del/<int:pk>/', self.wrapper(self.delete_view), name=self.get_del_url_name),
        ]

        extra = self.extra_url()
        if extra:
            urlpatterns.extend(extra)

        return urlpatterns

    def extra_url(self):
        pass

    @property
    def get_add_url_name(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_add' % (app_label,model_name,self.prev)
        else:
            name = '%s_%s_add' % (app_label,model_name)
        return name

    @property
    def get_list_url_name(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_changelist' % (app_label,model_name,self.prev)
        else:
            name = '%s_%s_changelist' % (app_label,model_name)
        return name

    @property
    def get_change_url_name(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_change' % (app_label,model_name,self.prev)
        else:
            name = '%s_%s_change' % (app_label,model_name)
        return name

    @property
    def get_del_url_name(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        if self.prev:
            name = '%s_%s_%s_del' % (app_label,model_name,self.prev)
        else:
            name = '%s_%s_del' % (app_label,model_name)
        return name
    def reverse_list_url(self):
        namespace = self.size.namespace
        name = '%s:%s' % (namespace,self.get_list_url_name)
        list_url = reverse(name)

        origin_condition = self.request.GET.get(self.back_condition_key)
        if not origin_condition:
            return list_url
        list_url = "%s?%s" % (list_url, origin_condition)
        return list_url

    def reverse_add_url(self):
        namespace = self.size.namespace
        name = '%s:%s' % (namespace,self.get_add_url_name)
        add_url = reverse(name)

        if not self.request.GET:
            return add_url
        param_str = self.request.GET.urlencode()  # 获取基础url后面的参数、
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        add_url = "%s?%s" % (add_url, new_query_dict.urlencode(),)
        return add_url

    def reverse_edit_url(self, row):
        namespace = self.size.namespace
        name = '%s:%s' % (namespace, self.get_change_url_name)
        edit_url = reverse(name, kwargs={'pk': row.pk})
        if not self.request.GET:
            return edit_url
        param_str = self.request.GET.urlencode()  # 获取基础url后面的参数、
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        edit_url = "%s?%s" % (edit_url, new_query_dict.urlencode(),)
        return edit_url

    def reverse_del_url(self, row):
        namespace = self.size.namespace
        name = '%s:%s' % (namespace, self.get_del_url_name)
        del_url = reverse(name, kwargs={'pk': row.pk})
        if not self.request.GET:
            return del_url
        param_str = self.request.GET.urlencode()  # 获取基础url后面的参数、
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        del_url = "%s?%s" % (del_url, new_query_dict.urlencode(),)
        return del_url
    @property
    def urls(self):
        return self.get_urls()


class AdminSite(object):

    def __init__(self):
        self._registry = []
        self.app_name = 'stark'
        self.namespace = 'stark'

    def register(self, model_class, stark_config=None,prev = None):
        # print(99999)
        if not stark_config:
            stark_config = StarkConfig
        self._registry.append(ModelConfigMapping(model_class,stark_config(model_class,self,prev),prev))

    def get_urls(self):
        urlpatterns = []
        # urlpatterns.append(path('x1/',self.x1))

        for item in self._registry:
            app_label = item.model._meta.app_label
            model_name = item.model._meta.model_name
            # print(model_name)
            if item.prev:
                temp = path('{}/{}/{}/'.format(app_label, model_name,item.prev ), (item.config.urls, None, None))
            else:
                temp = path('{}/{}/'.format(app_label, model_name, ), (item.config.urls, None, None))

            urlpatterns.append(temp)
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = AdminSite()
