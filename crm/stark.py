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
from crm.config.customer import CustConfig,PrivateCustConfig,PublicCustConfig
from crm.config.ConsultRecord import ConsultConfig,PirConsultConfig
from crm.config.student import StuConfig
from crm.config.course_record import CourseRecordConfig
from crm.config.StudyRecord import StudyRecordConfig
site.register(Department, DepConfig)

site.register(UserInfo, UserConfig)

site.register(Course,CourConfig)

site.register(School,SchoolConfig)
site.register(ClassList,Class_listConfig)

site.register(Customer,CustConfig)
site.register(Customer,PublicCustConfig,'pub')
site.register(Customer,PrivateCustConfig,'pri')

site.register(ConsultRecord,ConsultConfig)
site.register(ConsultRecord,PirConsultConfig,'pri')

site.register(Student,StuConfig)
site.register(CourseRecord,CourseRecordConfig)
site.register(StudyRecord,StudyRecordConfig)