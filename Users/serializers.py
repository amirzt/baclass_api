from rest_framework import serializers

from Users.models import CustomUser, Wallet, Student, Grade, Banner, HomeMessage, Version


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone', 'is_student', 'version']

    def save(self, **kwargs):
        user = CustomUser(phone=self.validated_data['phone'],
                          is_student=self.validated_data['is_student'],
                          version=self.validated_data['version'])
        user.save()

        # wallet
        wallet = Wallet(user=user)
        wallet.save()

        if user.is_student:
            student = Student(user=user,
                              grade=Grade.objects.all().first())
            student.save()

        return user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    wallet = serializers.SerializerMethodField('get_wallet')

    @staticmethod
    def get_wallet(self):
        return WalletSerializer(Wallet.objects.get(user=self)).data

    class Meta:
        model = CustomUser
        fields = ['phone', 'name', 'user_name', 'email', 'wallet', 'is_student', 'market', 'version']


class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    grade = GradeSerializer()

    class Meta:
        model = Student
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class HomeMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeMessage
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'
