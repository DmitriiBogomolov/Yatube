from django.test import TestCase, Client
from django.contrib.auth.models import User
from posts.models import Group, Post
from django.shortcuts import reverse as rv

# Create your tests here.

class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()

    def test_profile_page(self):

        response = self.client.get(
                    rv("profile", kwargs={"username": "testuser"})
                )
        self.assertEqual(response.status_code, 404)

        self.client.post(
                    rv("signup"),
                    {
                        "username": "testuser",
                        "email": "testuser@yandex.ru",
                        "password1": "aFASfaf124124",
                        "password2": "aFASfaf124124"
                    }
                )

        response = self.client.get(
                    rv("profile", kwargs={"username": "testuser"})
                )
        self.assertEqual(response.status_code, 200)


class TestPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        username="testuser",
                        email="testuser@yandex.ru",
                        password="12345",
                        first_name="Dmitrii",
                        last_name="Bogomolov"
        )

        self.post = Post.objects.create(
                        text="testpost",
                        author=self.user
        )
        self.group = Group.objects.create(
            title="testgroup",
            slug="testgroup"
        )

    def test_new_post_protect(self):
        response = self.client.get(rv("new_post"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(rv("login")))

        response = self.client.post(
                rv("new_post"),
                {"group": self.group.pk, "text": "skynetMyLove"}
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(rv("login")))

        self.assertFalse(Post.objects.filter(text="skynetMyLove"))

    def test_new_post(self):
        self.client.force_login(self.user)
        response = self.client.get(rv("new_post"))
        self.assertEqual(response.status_code, 200)

        newpost = self.client.post(
                rv("new_post"),
                {"group": self.group.pk, "text": "skynetMyLove"}
            )
        post = Post.objects.all().reverse()[0]
        self.assertEqual(post.author, self.user)

    def test_new_post_display(self):
        self.client.force_login(self.user)
        self.client.post(
                rv("new_post"),
                {"group": self.group.pk, "text": "skynetMyLove"}
            )

        post_id = Post.objects.count()
        post = Post.objects.all()[post_id-1]

        self.check_post_on_pages(post, post_id)

    def test_post_edit_protect(self):
        response = self.client.get(
                   rv(
                       "post_edit",
                        kwargs={
                            "username": "testuser",
                            "post_id": 1
                        }
                     )
                )
      
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(rv("login")))

        response = self.client.post(
                rv("post_edit", 
                   kwargs={
                       "username": "testuser",
                       "post_id": 1
                       }
                    ),
                {"text": "edited"}
            )

        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        response = self.client.post(
                rv("new_post"),
                {"group": self.group.pk, "text": "skynetMyLove"}
            )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(rv("index")))

        response = self.client.post(
                rv("post_edit",
                   kwargs={
                       "username": "testuser",
                       "post_id": 1
                       }
                    ),
                {"text": "edited"}
            )
    
        self.assertRedirects(
            response,
            rv("post", kwargs={"username": "testuser", "post_id": 1}),
            status_code=302, 
            target_status_code=200
        )

    def test_post_edit_display(self):
        self.client.force_login(self.user)
        self.client.post(
                    rv("new_post"),
                    {"group": self.group.pk, "text": "skynetMyLove"}
                )

        post_id = Post.objects.count()

        self.client.post(
                rv("post_edit", 
                   kwargs={
                       "username": "testuser",
                       "post_id": post_id
                       }
                    ),
                {"text": "edited"}
            )

        post = Post.objects.get(id=post_id)
        self.check_post_on_pages(post, post_id)

    # Check post is displayed on pages
    def check_post_on_pages(self, post, post_id):
        # Testing index page ########
        response = self.client.get(rv("index"))

        self.assertContains(
            response,
            f'Автор: {self.user.first_name} {self.user.last_name}'
        )

        self.assertContains(
            response,
            post.text
        )



        # Testing profile page ########
        response = self.client.get(
                rv("profile",
                   kwargs={"username": self.user.username}
                )
            )

        # Check contains post edit href
        self.assertContains(
            response,
            f'href="{rv("post_edit", kwargs={"username": self.user.username, "post_id": post_id})}'
        )

        # Check contains post href
        self.assertContains(
            response,
            f'href="{rv("post", kwargs={"username": self.user.username, "post_id": post_id})}'
        )

        # Check contains username / post.text
        self.assertContains(response, "@"+self.user.username)
        self.assertContains(response, post.text)



        # Testing post page ########
        response = self.client.get(
                rv(
                    "post",
                    kwargs={
                        "username": self.user.username,
                        "post_id": post_id
                    }
                )
            )

        self.assertContains(response, "@"+self.user.username)
        self.assertContains(response, post.text)

        self.assertContains(
            response,
            f'href="{rv("post_edit", kwargs={"username": self.user.username, "post_id": post_id})}'
        )