from rest_framework import serializers, status

from posts.models import Post, Comment, Group, Follow, User


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.ReadOnlyField(source='post.id')

    class Meta:
        fields = '__all__'
        model = Comment


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    following = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        fields = ('user', 'following', )
        model = Follow

    def validate_following(self, value):
        current_user = self.context['request'].user  # пользователь, который делает запрос на подписку
        current_following = Follow.objects.filter(user=current_user, following__username=value)  # подписка

        if current_following:
            raise serializers.ValidationError('нельзя подписываться дважды', code=status.HTTP_400_BAD_REQUEST)

        return value
