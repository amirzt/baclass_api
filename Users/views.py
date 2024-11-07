import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from AI.models import Prompt
from AI.serializers import PromptSerializer
from Users.models import CustomUser, Student, OTP, Grade, HomeMessage, Banner, Version, SMSToken, InAppMessage
from Users.serializers import RegisterSerializer, StudentSerializer, CustomUserSerializer, HomeMessageSerializer, \
    BannerSerializer, VersionSerializer, InAppMessageSerializer
from rest_framework.decorators import action
import requests

from utils.calculate_scores import calculate_score


def send_otp(user):
    api_url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"

    otp = OTP(user=user)
    otp.save()

    headers = {
        'Content-Type': 'application/json',
        'apikey': SMSToken.objects.filter().last().token
    }

    body = {
        "recipient": user.phone,
        "sender": SMSToken.objects.filter().last().number,
        "code": SMSToken.objects.filter().last().pattern,
        "variable": {
            "code": otp.code
        }
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(body))
    print(response)


class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        method = request.data.get('action')
        if not method:
            return Response({'error': 'action is required'}, status=status.HTTP_400_BAD_REQUEST)

        if method == 'login':
            try:
                user = CustomUser.objects.get(phone=request.data['phone'])
            except CustomUser.DoesNotExist:
                serializer = RegisterSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                else:
                    return Response(serializer.errors)
            send_otp(user)
            return Response({'message': 'otp sent'}, status=status.HTTP_200_OK)

        elif method == 'check_otp':
            user = get_object_or_404(CustomUser, phone=request.data['phone'])
            otp_code = request.data.get('otp')
            if not otp_code:
                return Response({'error': 'otp is required'}, status=status.HTTP_400_BAD_REQUEST)

            otp = OTP.objects.filter(user=user).last()
            if not otp or otp.code != otp_code:
                return Response({'error': 'invalid or expired otp'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = get_object_or_404(CustomUser, id=request.user.id)

        if request.method == 'GET':
            serializer = StudentSerializer(user.student) if user.is_student else CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            data = request.data
            if user.is_student:
                student = get_object_or_404(Student, user=user)
                if 'grade' in data:
                    student.grade = get_object_or_404(Grade, id=data['grade'])
                if 'gender' in data:
                    student.gender = data['gender']
                student.save()

            # Update the user fields
            user.name = data.get('name', user.name)
            user.user_name = data.get('user_name', user.user_name)
            user.email = data.get('email', user.email)
            user.market = data.get('market', user.market)
            user.version = data.get('version', user.version)
            user.save()

            return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def home(self, request):
        home_messages = HomeMessage.objects.filter(is_active=True).order_by('-created_at')
        banners = Banner.objects.filter(is_active=True).order_by('-created_at')
        version = Version.objects.all().last()
        prompts = Prompt.objects.filter(is_active=True)

        return Response({
            'home_messages': HomeMessageSerializer(home_messages, many=True).data,
            'banners': BannerSerializer(banners, many=True).data,
            'version': VersionSerializer(version).data,
            'prompts': PromptSerializer(prompts, many=True).data
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def splash(self, request):
        user = get_object_or_404(CustomUser, id=request.user.id)
        user.version = request.data['version']
        user.market = request.data['market']
        user.save()
        calculate_score(user, 'open_app')
        return Response(status=status.HTTP_200_OK)


class InAppMessageViewSet(viewsets.ModelViewSet):
    serializer_class = InAppMessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = InAppMessage.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_read']

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get_queryset(self):
        return self.queryset.filter(user=self.get_user())

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return Response(status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer(self, queryset, many):
        return self.serializer_class(queryset, many=many)
