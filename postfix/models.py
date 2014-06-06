from django.db import models
from crypt import crypt
import random

class Domain(models.Model):
    domain = models.CharField(max_length=255, primary_key=True)
    backupmx = models.BooleanField()
    modified = models.DateTimeField(auto_now_add=True)
    maxquota = models.IntegerField()
    quota = models.IntegerField()
    transport = models.CharField(max_length=255)
    active = models.BooleanField()

    def __unicode__(self):
        return self.domain
        
class Alias(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    goto = models.TextField()
    domain = models.ForeignKey(Domain, db_column='domain')
    modified = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField()
                
class Mailbox(models.Model):
    username = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    quota = models.IntegerField()
    maildir = models.CharField(max_length=255)
    modified = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField()
    domain = models.ForeignKey(Domain, db_column='domain')

    def save(self, *args, **kwargs):
        self.maildir = self.username + "/"
        random.seed()
        hash = random.getrandbits(32)
        salt = '$1$%08x' % hash
        self.password = crypt(self.password, salt)
        super(Mailbox, self).save(*args, **kwargs) # Call the "real" save() method.





