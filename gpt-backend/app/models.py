from uuid import uuid4
from tortoise.models import Model
from tortoise import fields


class SystemPrompt(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField()
    content = fields.TextField()
    contexts: fields.ReverseRelation["Context"]


class User(Model):
    create_time = fields.DatetimeField(auto_now_add=True)
    openid = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    avatar = fields.TextField()
    balance = fields.FloatField()
    contexts: fields.ReverseRelation["Context"]


class Context(Model):
    id = fields.IntField(pk=True)
    session_id = fields.UUIDField(index=True,default=uuid4)
    summary = fields.CharField(max_length=255, null=True)
    create_time = fields.DatetimeField(auto_now_add=True)
    content = fields.JSONField(default=[], null=True)
    prompt = fields.ForeignKeyField(
        "models.SystemPrompt", related_name="context", null=True
    )
    user = fields.ForeignKeyField("models.User", related_name="context")

    class Meta:
        ordering = ["create_time"]
