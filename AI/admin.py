from django.contrib import admin

from AI.models import ApiKey, Chat, ChatMessage, Prompt

# Register your models here.
admin.site.register(ApiKey)

admin.site.register(Chat)

admin.site.register(ChatMessage)

admin.site.register(Prompt)
