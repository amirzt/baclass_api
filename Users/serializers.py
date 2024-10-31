from rest_framework import serializers

from Users.models import CustomUser, Wallet, Student, Grade


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone', 'is_student', 'version', 'market']

    def save(self, **kwargs):
        user = CustomUser(phone=self.validated_data['phone'],
                          is_student=self.validated_data['is_student'],
                          version=self.validated_data['version'],
                          market=self.validated_data['market'])
        user.save()

        # wallet
        wallet = Wallet(user=user)
        wallet.save()

        if user.is_student:
            student = Student(user=user,
                              grade=Grade.objects.all().first())
            student.save()

        return user
