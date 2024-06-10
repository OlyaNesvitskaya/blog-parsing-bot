from rest_framework import serializers

from web.models import Article, ParsingArticle, Profile


class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'publication_date', 'url', 'profile')

    @staticmethod
    def get_url(obj):
        return 'http://127.0.0.1:8000/web/article_detail/' + str(obj.id)


class ArticlePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('id', 'title', 'publication_date', 'profile')


class LatestArticleSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'publication_date', 'url')

    @staticmethod
    def get_url(obj):
        return 'http://127.0.0.1:8000/web/article_detail/' + str(obj.get('id'))


class ParsingArticlesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="headline")

    class Meta:
        model = ParsingArticle
        fields = ('id', 'title', 'url')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = Profile
        fields = ('username', 'avatar')


class ArticleParamValidationSerializer(serializers.Serializer):
    id_from = serializers.IntegerField(error_messages={'invalid': 'Your id_from must be a number'},
                                       required=False)
    id_to = serializers.IntegerField(error_messages={'invalid': 'Your id_to must be a number'},
                                     required=False)
