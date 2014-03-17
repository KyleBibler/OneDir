from django.db import models

# Create your models here.


class User(models.Model):
	userName = models.CharField(max_length=200)
	userPassword = models.CharField(max_length=200)

	def __unicode__(self):
		return self.userName

class File(models.Model):
	fileName = models.CharField(max_length=200)
	fileOwner = models.ForeignKey(User)
	fileSize = models.IntegerField(default=0)

	def __unicode__(self):
		return self.fileName