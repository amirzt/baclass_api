from django.db import models

from Users.models import CustomUser


# Create your models here.

class ApiKey(models.Model):
    class Type(models.TextChoices):
        gpt = 'gpt', 'GPT'
        gemini = 'gemini', 'Gemini'

    key = models.CharField(max_length=1000, null=False, blank=False)
    type = models.CharField(max_length=10, choices=Type.choices, null=False, blank=False, default=Type.gemini)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Chat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    summary = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    class Sender(models.TextChoices):
        user = 'user', 'User'
        bot = 'bot', 'bot'
        system = 'system', 'System'

    class BotType(models.TextChoices):
        gpt = 'gpt', 'GPT'
        gemini = 'gemini', 'Gemini'

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.CharField(max_length=10000, null=False, blank=False)
    sender = models.CharField(max_length=10, choices=Sender.choices, null=False, blank=False, default=Sender.user)
    bot = models.CharField(max_length=10, choices=BotType.choices, null=False, blank=False, default=BotType.gpt)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Prompt(models.Model):
    name = models.CharField(max_length=1000, null=False, blank=False)
    short_desc = models.CharField(max_length=1000, null=False, blank=False)
    prompt = models.CharField(max_length=10000, null=False, blank=False)
    logo = models.ImageField(upload_to='ai/prompts', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
