from openai import OpenAI

from AI.models import ChatMessage, ApiKey
from AI.serializers import ApiMessageSerializer


def ask_question(chat):
    api_key = ApiKey.objects.get(type=ApiKey.Type.gpt).key
    client = OpenAI(api_key=api_key)

    messages = ChatMessage.objects.filter(chat=chat).order_by('-created_at')
    serializer = ApiMessageSerializer(messages, many=True)
    print(messages)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=serializer.data
    )

    bot_message = ChatMessage(chat=chat,
                              message=completion.choices[0].message.content,
                              sender=ChatMessage.BotType.gpt)

    bot_message.save()
    return bot_message
