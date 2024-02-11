from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


from datetime import datetime


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # связь с встроенной моделью пользователей User;
    ratingAuthor = models.SmallIntegerField(default=0)  # рейтинг пользователя

    def update_rating(self):
        post_rating = self.posts.aggregate(pr=Coalesce(Sum('rating'), 0)).get('pr')
        comments_rating = self.user.comment.aggregate(cr=Coalesce(Sum('rating'), 0))['cr']
        posts_comments_rating = self.posts.aggregate(pcr=Coalesce(Sum('comment__rating'), 0))['pcr']

        self.ratingAuthor = post_rating * 3 + comments_rating + posts_comments_rating
        self.save()


# def viv(self):
#     # a = Author.objects.values.order_by('-ratingAuthor')[:1]
#     #  a = Author.objects.order_by("-ratingAuthor").values_list("user__user", "ratingAuthor")[0]
#     a = a1.post_set.aggregate(Sum('rating')).get('rating__sum')
#     print(a)

class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True)  # Категории новостей/статей


class Post(models.Model):
    author = models.ForeignKey(Author,
                               on_delete=models.CASCADE,
                               related_name='posts')  # связь «один ко многим» с моделью Author;
    NEWS = 'NE'  # поле с выбором — «статья» или «новость»;
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'))
    post_type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    post_time = models.DateTimeField(auto_now_add=True)  # автоматически добавляемая дата и время создания;
    category = models.ManyToManyField(Category, through='PostCategory')  # связь с моделью Category, PostCategory
    title = models.CharField(max_length=255)  # заголовок статьи/новости;
    text = models.TextField()  # текст статьи/новости;
    rating = models.IntegerField(default=0)  # рейтинг статьи/новости.

    def preview(self):  # возвращает начало статьи (предварительный просмотр)
        post_preview = f'{self.text[0:123]}...'
        return post_preview

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    # def view(self):  # возвращает
        # x = Post.objects.order_by('-rating')[0].comment_set.values('comment_time', 'comment_user__username', 'rating', 'text')
        # x = Post.objects.order_by('-rating')[0].comment_set.all().values('comment_time', 'comment_user__username',
        #                                                                  'rating', 'text')
        # self.preview()
        # return x
        #
        # Post.objects.order_by('-rating')[0].comment_set.values('rating')

        # post_view = f'{self.objects.order_by('-rating')[:1]}...'
        # print(f'{p.rating} {p.author}')
        # return post_view


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # связь «один ко многим» с моделью Post;
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # связь «один ко многим» с моделью Category.


class Comment(models.Model):
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)  # связь с моделью Post;
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment')  # связь с моделью User
    text = models.TextField()  # текст комментария;
    comment_time = models.DateTimeField(auto_now_add=True)  # дата и время создания комментария;
    rating = models.IntegerField(default=0)  # рейтинг комментария.

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
