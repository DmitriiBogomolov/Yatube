from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk}: {self.title}"


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
                    "date published",
                    auto_now_add=True,
                    db_index=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="author_posts")
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name="group_posts",
                              verbose_name="Группа")
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(
                    Post,
                    related_name="comment_post",
                    on_delete=models.CASCADE
    )
    author = models.ForeignKey(
                    User,
                    related_name="comment_author",
                    on_delete=models.CASCADE
    )
    text = models.TextField(verbose_name="comment_text")
    created = models.DateTimeField("date_created", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
                User,
                related_name="follower",
                on_delete=models.CASCADE
    )
    author = models.ForeignKey(
                User,
                related_name="following",
                on_delete=models.CASCADE
    )
