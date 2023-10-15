from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register 

from .models import Post

class PostAdmin(ModelAdmin):
    model = Post
    menu_label = 'Post'
    menu_icon = 'pick'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ('title', 'created', 'author',)
    list_filter = ('title', 'created',)
    search_fields = ('title',)
    prepopulated_fields = { 'slug': ('title',)}
    
modeladmin_register(PostAdmin)
    