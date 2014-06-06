from django.db import models

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length = 64 )
    last_name = models.CharField(max_length = 64)
    email = models.EmailField(max_length = 64)
    add_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    response = models.TextField()
    responded = models.BooleanField(default=False)