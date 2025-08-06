from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Count, Sum


class UserListSerializer(serializers.ModelSerializer):
    posts_written = serializers.IntegerField()
    followers_count = serializers.IntegerField()
    posts_reactions = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "posts_written",
            "posts_reactions",
            "followers_count",
        )

    def get_posts_reactions(self, obj):
        return {"Liked": obj.total_likes, "Disliked": obj.total_dislikes}

    def get_followers(self, obj):
        return {"count": obj.followers_count}


class UserRetrieveSerializer(UserListSerializer):
    followers = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "is_staff",
            "image",
            "about_me",
            "posts_written",
            "posts_reactions",
            "following",
            "followers",
        )

    def get_followers(self, obj):
        return {
            "count": obj.followers_count,
            "emails": list(obj.followers.values_list("email", flat=True)),
        }


class UserUpdateSerializer(UserRetrieveSerializer):
    posts_written = serializers.IntegerField(read_only=True)

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

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
