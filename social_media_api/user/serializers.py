from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Count, Sum


class UserSerializer(serializers.ModelSerializer):
    posts_written = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    posts_reactions = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "image",
            "about_me",
            "posts_written",
            "posts_reactions",
            "following",
            "followers",
        )
        read_only_fields = ("id", "is_staff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_posts_written(self, obj):
        return obj.posts.count()

    def get_followers(self, obj):
        return f"{obj.followers.count()} / {list(obj.followers.values_list('email', flat=True))}"

    def get_posts_reactions(self, obj):
        posts = obj.posts.annotate(
            num_likes=Count("liked"), num_dislikes=Count("disliked")
        )
        reactions = posts.aggregate(Sum("num_likes"), Sum("num_dislikes"))
        return f"Liked:{reactions['num_likes__sum'] or 0} / Disliked:{reactions['num_dislikes__sum'] or 0}"

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
