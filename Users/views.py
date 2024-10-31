from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Users.models import CustomUser, Student, OTP, Grade
from Users.serializers import RegisterSerializer, StudentSerializer, CustomUserSerializer


def send_otp(user):
    otp = OTP(user=user)
    otp.save()


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if 'action' in request.data:
        action = request.data['action']
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'action is required'})

    if action == 'login':
        try:
            user = CustomUser.objects.get(phone=request.data['phone'])
        except CustomUser.DoesNotExist:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        send_otp(user)
        return Response(status=status.HTTP_200_OK, data={'message': 'otp sent'})
    elif action == 'check_otp':
        user = CustomUser.objects.get(phone=request.data['phone'])
        if 'otp' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'otp is required'})
        otp = OTP.objects.filter(user=user)
        if otp.count() == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'otp not found'})
        if request.data['otp'] != otp.last().code:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'invalid otp'})
        else:
            user.is_active = True
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(status=status.HTTP_200_OK, data={'token': token.key})

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'invalid action'})


@api_view(['PUT', 'GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    if request.method == 'GET':
        if user.is_student:
            student = Student.objects.get(user=user)
            serializer = StudentSerializer(student)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_200_OK, data=CustomUserSerializer(user).data)
    elif request.method == 'PUT':
        if user.is_student:
            student = Student.objects.get(user=user)
            if 'grade' in request.data:
                student.grade = Grade.objects.get(id=request.data['grade'])
            if 'gender' in request.data:
                student.gender = request.data['gender']
            student.save()
        if 'name' in request.data:
            user.name = request.data['name']
        if 'user_name' in request.data:
            user.user_name = request.data['user_name']
        if 'email' in request.data:
            user.email = request.data['email']
        if 'market' in request.data:
            user.market = request.data['market']
        if 'version' in request.data:
            user.version = request.data['version']
        user.save()
        return Response(status=status.HTTP_200_OK)
