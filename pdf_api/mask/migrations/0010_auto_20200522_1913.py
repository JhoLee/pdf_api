# Generated by Django 3.0.3 on 2020-05-22 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mask', '0009_auto_20200522_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maskrequest',
            name='seg_method',
            field=models.CharField(choices=[('deeplabv3_resnet101', 'DeepLabV3'), ('fcn_resnet101', 'FCN')], default='deeplabv3_resnet101', max_length=30),
        ),
    ]