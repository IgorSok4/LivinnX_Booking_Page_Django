from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import Post


class PostDetailView(DetailView):
    template_name = 'blog/post_detail.html'
    model = Post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_post = get_object_or_404(Post, slug=self.kwargs['slug'])
        context['next_post'] = Post.objects.filter(id__gt=current_post.id).order_by('id').first()
        context['prev_post'] = Post.objects.filter(id__lt=current_post.id).order_by('-id').first()
        print(context)
        return context
    
