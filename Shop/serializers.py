from rest_framework import serializers

from Shop.models import Package, Transaction


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class AddTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['price', 'gateway', 'gateway_code', 'description', 'user', 'package']

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)
