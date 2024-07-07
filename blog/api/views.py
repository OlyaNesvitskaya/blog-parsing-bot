from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from web.models import Article, ParsingArticle
from .serializers import (
    ArticleSerializer,
    ArticlePostSerializer,
    LoginSerializer,
    LatestArticleSerializer,
    ArticleParamValidationSerializer,
    ParsingArticlesSerializer
)
from rest_framework.authtoken.models import Token


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit  or deleteit.
    Assumes the model instance has an `profile` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.profile == request.user


class ApiArticle(generics.ListCreateAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticlePostSerializer
        parsing_param = self.request.query_params.get("parsing")
        if parsing_param == '1':
            return ParsingArticlesSerializer
        return ArticleSerializer

    def get_queryset(self):

        is_parsing = self.request.query_params.get('parsing')
        queryset = ParsingArticle.objects.all() if is_parsing == '1' else Article.objects.all()

        serializer = ArticleParamValidationSerializer( data=self.request.query_params )
        serializer.is_valid(raise_exception=True)

        id_from = self.request.query_params.get('id_from')
        id_to = self.request.query_params.get('id_to')

        if id_from is not None and id_to is not None:
            queryset = queryset.filter(pk__range=(int(id_from), int(id_to)))
        elif id_from is not None:
            queryset = queryset.filter(pk__gte=int(id_from))
        elif id_to is not None:
            queryset = queryset.filter(pk__lte=int(id_to))

        return queryset


class ApiArticleDetail(generics.RetrieveUpdateDestroyAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class ApiLatestArticleDetail(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_article = Article.objects.values('id', 'title', 'publication_date').latest('publication_date')
            serializer = LatestArticleSerializer(latest_article)
            return Response(serializer.data)
        except:
            return Response({})


class ApiLatestParsingArticle(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_article = ParsingArticle.objects.latest('added_date')
            serializer = ParsingArticlesSerializer(latest_article)
            return Response(serializer.data)
        except:
            return Response({})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def logout_view(request):
    request.auth.delete()  # Delete the token upon logout
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

