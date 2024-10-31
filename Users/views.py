from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser, Student, OTP, Grade
from Users.serializers import RegisterSerializer, StudentSerializer, CustomUserSerializer
from rest_framework.decorators import action


def send_otp(user):
    otp = OTP(user=user)
    otp.save()


class UserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        method = request.data.get('action')
        if not method:
            return Response({'error': 'action is required'}, status=status.HTTP_400_BAD_REQUEST)

        if method == 'login':
            user, created = CustomUser.objects.get_or_create(phone=request.data['phone'])
            if created:
                serializer = RegisterSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
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