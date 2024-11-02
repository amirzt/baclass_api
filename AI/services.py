from openai import OpenAI

from AI.models import ChatMessage, ApiKey
from AI.serializers import ApiMessageSerializer


def ask_question(chat):
    api_key = ApiKey.objects.get(type=ApiKey.Type.gpt).key
    client = OpenAI(api_key=api_key)

    messages = ChatMessage.objects.filter(chat=chat).order_by('-created_at')
    serializer = ApiMessageSerializer(messages, many=True)

    print(serializer.data)
    # completion = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=serializer.data
    # )
    #
    # print(completion.choices[0].message)
