from django.contrib import admin
from .models import Profile, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'active',)
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display= ('user', 'created', 'text')
    list_filter = ('user',)
    search_fields = ('user', 'text')