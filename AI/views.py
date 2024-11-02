from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from AI.models import Chat
from AI.serializers import MessageSerializer, ChatSerializer
from AI.services import ask_question
from Users.models import CustomUser


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def get_user(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        chat_id = request.data.get('chat')
        data = request.data.copy()

        if not chat_id:
            serializer = self.get_serializer(data=request.data, context={'user': self.get_user()})
            serializer.is_valid(raise_exception=True)
            chat = serializer.save()
        else:
            chat = get_object_or_404(Chat, id=chat_id)
            data['chat'] = chat.id

        message_serializer = MessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)
        message_serializer.save(chat=chat)

        ask_question(chat)

        return Response(data={"chat_id": chat.id})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='messages')
    def get_messages(self, request, pk=None):
        chat = self.get_object()  # Fetches the Chat instance by `pk`
        messages = chat.chatmessage_set.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
