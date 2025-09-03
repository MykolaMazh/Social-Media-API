from celery import shared_task


@shared_task
def post_publish(post):
    post.is_published = True
    post.save()
    return post
