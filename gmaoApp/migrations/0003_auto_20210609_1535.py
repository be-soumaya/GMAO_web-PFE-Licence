# Generated by Django 3.2.1 on 2021-06-09 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gmaoApp', '0002_planpreventive_etat_planning'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intervention',
            name='pieces_utilisees',
        ),
        migrations.AddField(
            model_name='intervention',
            name='pieces_utilisees',
            field=models.ManyToManyField(blank=True, null=True, to='gmaoApp.Pdr'),
        ),
    ]
