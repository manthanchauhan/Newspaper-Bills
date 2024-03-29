# Generated by Django 2.2.1 on 2019-06-08 06:18

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('message', models.TextField(max_length=1000)),
                ('image', models.ImageField(upload_to='feedback/%Y/%m/%d', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'png', 'tif', 'gif'])])),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
