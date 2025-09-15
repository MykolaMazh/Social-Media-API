from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "password",
            "image",
            "about_me",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


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


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email"]


class UserRetrieveSerializer(UserListSerializer):
    followers = serializers.SerializerMethodField()
    following = UserShortSerializer(many=True, read_only=True)

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
    following = serializers.PrimaryKeyRelatedField(
        many=True, queryset=get_user_model().objects.all()
    )

    class Meta:
        model = get_user_model()
        fields = (
            "password",
            "image",
            "about_me",
            "following",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        following_data = validated_data.pop("following", None)
        user = super().update(instance, validated_data)

        if following_data is not None:
            instance.following.set(following_data)

        if password:
            user.set_password(password)
            user.save()

        return user
