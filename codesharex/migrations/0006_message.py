# Generated by Django 3.2.18 on 2023-05-14 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codesharex', '0005_auto_20230514_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=256)),
                ('time', models.IntegerField()),
                ('app_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codesharex.appuser')),
                ('belongs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codesharex.content')),
            ],
            options={
                'verbose_name': '用户消息',
                'verbose_name_plural': '用户消息',
            },
        ),
    ]
