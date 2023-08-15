from django.contrib import admin
from .models import Post, DocAttachment, ImgAttachment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'title')
    search_fields = ('title', 'body')
    prepopulated_fields = { 'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    
@admin.register(DocAttachment)
class DocAttachmentAdmin(admin.ModelAdmin):
    list_display = ('doc_name',)
    
@admin.register(ImgAttachment)
class ImgAttachmentAdmin(admin.ModelAdmin):
    list_display = ('img_name',)