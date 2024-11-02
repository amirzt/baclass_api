from rest_framework import serializers

from AI.models import ChatMessage, Chat


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'sender', 'bot', 'chat']

    def create(self, validated_data):
        return ChatMessage.objects.create(**validated_data)


class ApiMessageSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source='message')
    role = serializers.CharField(source='sender')

    class Meta:
        model = ChatMessage
        fields = ['content', 'role']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField('get_last_message')

    @staticmethod
    def get_last_message(obj):
        return MessageSerializer(ChatMessage.objects.filter(chat=obj).last()).data

    class Meta:
        model = Chat
        fields = ['id', 'summary', 'last_message', 'created_at', 'updated_at']

    def create(self, validated_data):
        return Chat.objects.create(user=self.context['user'], **validated_data)
