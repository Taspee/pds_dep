# Generated by Django 5.1 on 2024-11-10 16:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Usuario',
            new_name='User',
        ),
        migrations.CreateModel(
            name='Locker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lockers', to='lapp.user')),
            ],
        ),
        migrations.DeleteModel(
            name='Casillero',
        ),
    ]
