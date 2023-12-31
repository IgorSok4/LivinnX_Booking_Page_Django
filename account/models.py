from django.db import models
from django.conf import settings

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             on_delete=models.CASCADE, 
                             related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    sauna_active = models.BooleanField(default=True)
    jacuzzi_active = models.BooleanField(default=True)
    orange_active = models.BooleanField(default=True)
    blue_active = models.BooleanField(default=True)
    music_active = models.BooleanField(default=True)
    art_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d',
                              blank=True)
    
    def __str__(self):
        return f"{self.user.username} profile"
    