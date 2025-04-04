# Generated by Django 5.1.7 on 2025-03-30 14:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_schedule_task_schedule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='day_of_week',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='time_of_day',
        ),
        migrations.CreateModel(
            name='ScheduleMoment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('time_of_day', models.TimeField()),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moments', to='todo.schedule')),
            ],
        ),
    ]
