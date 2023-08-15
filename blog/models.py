from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# class PublishedManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(status='published')

class DocAttachment(models.Model):
    doc_name = models.CharField(max_length=50, blank=True)
    doc = models.FileField(upload_to='doc_attachments')
    
class ImgAttachment(models.Model):
    img_name = models.CharField(max_length=50, blank=True)
    image = models.FileField(upload_to='img_attachments')

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    POST_TYPE = (
        ('technical', 'Technical'),
        ('community', 'Community'),
        ('event', 'Event'),
        ('important', 'Important'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body_pl = models.TextField(null=True)
    body_en = models.TextField(null=True)
    body_ru = models.TextField(null=True)
    image = models.ImageField(upload_to='users/%Y/%m/%d',
                              blank=False,
                              default='default_photos\kox_corridor.jpg')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')
    type = models.CharField(max_length=20,
                            choices=POST_TYPE,
                            default='community')
    file = models.ForeignKey(DocAttachment,
                             on_delete=models.CASCADE, 
                             related_name='doc_attachments',
                             blank=True, null=True)
    image_file = models.ForeignKey(ImgAttachment,
                                   on_delete=models.CASCADE,
                                   related_name='img_attachments',
                                   blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    
    # objects = models.Manager()
    # published = PublishedManager()
    
    class Meta:
        ordering = ('-publish',)
        
    def __str__(self):
        return self.title