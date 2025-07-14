from django.db import models

# Create your models here.
class login_table(models.Model):
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    type=models.CharField(max_length=100)

class user_table(models.Model):
    LOGIN=models.ForeignKey(login_table,on_delete=models.CASCADE)
    uname=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    # pin=models.IntegerField()
    phone=models.BigIntegerField()
    email=models.CharField(max_length=100)
    image=models.FileField()


class post_table(models.Model):
    USER= models.ForeignKey(user_table, on_delete=models.CASCADE)
    image = models.FileField()
    description=models.CharField(max_length=100)
    date=models.DateField()
    location= models.CharField(max_length=100)


class theftinfo_table(models.Model):
    POST = models.ForeignKey(post_table, on_delete=models.CASCADE)
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE)
    status=models.CharField(max_length=100)



class Feedback(models.Model):
    USERNAME = models.ForeignKey(user_table,on_delete=models.CASCADE)
    date = models.DateField()
    feedback = models.CharField(max_length=40)
    rating = models.FloatField()

class Complaint(models.Model):
    USERNAME = models.ForeignKey(user_table,on_delete=models.CASCADE)
    complaint = models.CharField(max_length=100)
    date=models.DateField()
    replay=models.CharField(max_length=50)

class Request(models.Model):
    fromid = models.ForeignKey(login_table,on_delete=models.CASCADE,related_name='ll')
    status = models.CharField(max_length=40)
    toid = models.ForeignKey(login_table,on_delete=models.CASCADE,related_name='jjj')
    date = models.DateField()


class Chat(models.Model):
    fromid = models.ForeignKey(login_table, on_delete=models.CASCADE, related_name='kk')
    toid = models.ForeignKey(login_table,on_delete=models.CASCADE, related_name='mmm')
    date = models.DateField()
    message=models.CharField(max_length=40)


class Comment(models.Model):
    USERNAME = models.ForeignKey(user_table,on_delete=models.CASCADE)
    date = models.DateField()
    POSTID=models.ForeignKey(post_table,on_delete=models.CASCADE)
    comment=models.TextField()
    type=models.CharField(max_length=40,default="pending")

class Like(models.Model):
    POSTID=models.ForeignKey(post_table,on_delete=models.CASCADE)
    USER=models.ForeignKey(user_table,on_delete=models.CASCADE)
    likes=models.BigIntegerField()
    date=models.DateField()


class Post_Alert(models.Model):
    USERNAME = models.ForeignKey(user_table,on_delete=models.CASCADE)
    POSTID=models.ForeignKey(post_table,on_delete=models.CASCADE)
    status = models.CharField(max_length=40)
    date = models.DateField()


class theft_alert_table(models.Model):
    USER = models.ForeignKey(user_table, on_delete=models.CASCADE,related_name="usr")
    Theft_user = models.ForeignKey(user_table, on_delete=models.CASCADE,related_name="frm")
    status = models.CharField(max_length=200)
    date = models.CharField(max_length=200)


