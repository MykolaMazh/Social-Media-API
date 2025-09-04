from django.contrib import admin
from social_media.models import Tag, Post, Comment


class CommentInline(admin.TabularInline):  # or admin.StackedInline
    model = Comment
    extra = 1  # how many empty comment forms to show
    readonly_fields = ("created_at", "author", "content")  # optional


# Custom Post admin
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    inlines = [CommentInline]
    readonly_fields = (
        "title",
        "author",
        "content",
        "photo",
        "tags",
        "views",
        "created_at",
        "updated_at",
    )
    exclude = ["viewers", "liked", "disliked"]


# Register models
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
