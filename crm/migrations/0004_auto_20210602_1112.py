# Generated by Django 2.2.8 on 2021-06-02 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
        ('crm', '0003_auto_20210602_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('email', models.CharField(max_length=32, verbose_name='邮箱')),
                ('names', models.CharField(max_length=16, verbose_name='真实姓名')),
                ('phone', models.CharField(max_length=32, verbose_name='手机号')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别')),
                ('depart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Department', verbose_name='部门')),
                ('roles', models.ManyToManyField(blank=True, to='rbac.Role', verbose_name='拥有的所有角色')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='classlist',
            name='class_teacher',
            field=models.ForeignKey(limit_choices_to={'depart__title': '教育部'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='crm.UserInfo', verbose_name='班主任'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='tech_teachers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'depart__title__in': ['Linux教学部', 'Python教学部']}, null=True, related_name='teach_classes', to='crm.UserInfo', verbose_name='任课老师'),
        ),
    ]