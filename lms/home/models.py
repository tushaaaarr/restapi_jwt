from django.db import models
from django.contrib.auth.models import User 
from datetime import datetime,timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

# User types  
class user_type(models.Model):
    is_member = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        if self.is_member == True:
            return str(self.user) + str(' ') + " - is_member"
        elif self.is_librarian == True:
            return str(self.user) + str(' ') + " - is_librarian"

# Member 
class Member(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=10)
    def __str__(self):
        return str(self.name)

# Book table
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    summary = models.TextField(max_length=100)
    isbn = models.CharField('ISBN', max_length=13)
    quantity = models.IntegerField()
    def __str__(self):
        return self.title 

def get_expiry():
    return datetime.today() + timedelta(days=15)

# Borrower 
class Borrower(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    issue_date = models.DateTimeField(null=True,default=datetime.now())
    return_date = models.DateTimeField(default=get_expiry)
    def __str__(self):
        return self.member.name+" borrowed "+self.book.title




# Signals used to create profile instance 
@receiver(post_save, sender=Member)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_type.objects.create(user=instance.user,is_member = True)

@receiver(post_save, sender=Member)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.user_type.save()
    except:
        pass