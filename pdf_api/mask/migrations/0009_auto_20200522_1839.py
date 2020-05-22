# Generated by Django 3.0.3 on 2020-05-22 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mask', '0008_auto_20200518_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maskrequest',
            name='method',
        ),
        migrations.AddField(
            model_name='maskrequest',
            name='masking_method',
            field=models.CharField(choices=[('BL', 'Blurring')], default='BL', max_length=3),
        ),
        migrations.AddField(
            model_name='maskrequest',
            name='seg_method',
            field=models.CharField(choices=[('DLR', 'DeepLabV3_Resnet101'), ('FCNR', 'FCN_ResNet101')], default='DLR', max_length=5),
        ),
    ]
