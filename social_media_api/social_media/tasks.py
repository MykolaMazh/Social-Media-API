from celery import shared_task

from social_media.models import Post


@shared_task
def post_publish(post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.is_published = True
        post.save()
        return f"Post {post.id} published"
    except Post.DoesNotExist:
        return f"Post {post_id} not found"
