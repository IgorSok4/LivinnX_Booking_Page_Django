from django.contrib import admin
from .models import Profile, Comment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'active',)
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display= ('tenant', 'created', 'text')
    list_filter = ('tenant',)
    search_fields = ('tenant', 'text')