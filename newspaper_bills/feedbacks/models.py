from django.db import models
from bill_manager import models as app_models
from django.core.validators import FileExtensionValidator
from markdown import markdown
from django.utils.html import mark_safe


class Feedback(models.Model):
    user = models.ForeignKey(to=app_models.User, on_delete=models.SET_NULL,
                             null=True, related_name='feedback')
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    image = models.ImageField(null=True, upload_to='feedback/%Y/%m/%d', validators=[
        FileExtensionValidator(allowed_extensions=['jpeg',
                                                   'jpg',
                                                   'png',
                                                   'bmp',
                                                   ])])

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

