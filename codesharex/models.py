from django.db import models
from util.dateformat import dateformat

# Create your models here.
class AppUser(models.Model):
    nick_name = models.CharField(max_length=32, default='微信用户')
    openid = models.CharField(max_length=64)
    avatar = models.ImageField(blank=True, upload_to='images/avatar')

    def __str__(self) -> str:
        return f"{self.nick_name}({self.openid[:5]}...{self.openid[-5:]})"

    class Meta:
         verbose_name = "App用户"
         verbose_name_plural = "App用户"


class Content(models.Model):
    content = models.TextField()
    short = models.CharField(max_length=256)
    poster = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    lang = models.CharField(max_length=32)
    never_destory = models.BooleanField()
    destory_time = models.IntegerField()
    post_time = models.IntegerField()
    password = models.CharField(max_length=32, blank=True)

    def __str__(self) -> str:
        short = self.short.strip()
        l = len(short)
        return f"by {self.poster.nick_name}: {short[:16 if l>16 else l]} id:{self.pk}"

    class Meta:
         verbose_name = "页面"
         verbose_name_plural = "页面"
    

class Collect(models.Model):
    app_user = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    content = models.ForeignKey(to=Content, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.app_user.nick_name} -> {self.content.pk}"

    class Meta:
         verbose_name = "收藏"
         verbose_name_plural = "收藏"


class Comment(models.Model):
    app_user = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    to = models.IntegerField(null=True)
    belongs = models.ForeignKey(to=Content, on_delete=models.CASCADE)
    comment = models.CharField(max_length=512)
    time = models.IntegerField()

    def __str__(self) -> str:
        return f"on:{self.belongs.pk}  \"{self.comment}\"  \
        by:{self.app_user.nick_name}({self.app_user.openid[:5]}...{self.app_user.openid[-5:]})"

    class Meta:
         verbose_name = "评论"
         verbose_name_plural = "评论"


class Message(models.Model):
    sender_openid = models.CharField(max_length=64, default="")
    sender_name = models.CharField(max_length=32, default="微信用户")
    to_comment = models.IntegerField(null=True)
    app_user = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    belongs = models.ForeignKey(to=Content, on_delete=models.CASCADE)
    content = models.CharField(max_length=256)
    time = models.IntegerField()
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender_name} " + f"-> #{self.app_user.nick_name}" \
                + f" on:{self.belongs.pk} {dateformat(self.time)} #{self.pk}"

    class Meta:
         verbose_name = "用户消息"
         verbose_name_plural = "用户消息"