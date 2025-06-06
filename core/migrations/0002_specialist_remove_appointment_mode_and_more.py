# Generated by Django 5.2.1 on 2025-05-19 20:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Specialist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='mode',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='doctor',
            name='name',
        ),
        migrations.AddField(
            model_name='appointment',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='time',
            field=models.TimeField(),
        ),
        migrations.AddField(
            model_name='doctor',
            name='available_times',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='doctor',
            name='user',
            field=models.OneToOneField(
                default=1,  # ✅ Fix: assign to user with ID 1
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(),
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('gender', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.patient'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('method', models.CharField(choices=[('mpesa', 'M-Pesa'), ('stripe', 'Stripe')], max_length=50)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.appointment')),
            ],
        ),
        migrations.AlterField(
            model_name='doctor',
            name='specialty',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.specialist'),
        ),
        migrations.AlterField(
            model_name='symptomspecialtymap',
            name='specialty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.specialist'),
        ),
    ]
