from django.test import TestCase, Client
from django.contrib.auth.models import User
from posts.models import Group, Post, Follow
from django.shortcuts import reverse as rv


class TestFollows(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_follower = User.objects.create_user(
                        username="testuser_follower",
                        email="testuser@yandex.ru",
                        password="12345",
                        first_name="Dmitrii",
                        last_name="Bogomolov"
        )
        self.user_following = User.objects.create_user(
                        username="testuser_following",
                        email="testuser1@yandex.ru",
                        password="12345",
                        first_name="Dmitrii1",
                        last_name="Bogomolov1"
        )

        self.post = Post.objects.create(
                        text="testpost",
                        author=self.user_following
        )
        self.group = Group.objects.create(
            title="testgroup",
            slug="testgroup"
        )

    def test_follow_protect(self):
        self.assertFalse(Follow.objects.count())

        # check hrefs not exists
        response = self.client.get(
            rv("profile", kwargs={"username": "testuser_following"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            f'href="{rv("profile_follow", args=["testuser_following"])}"'
        )

        # try follow
        response = self.client.get(
            rv(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                }
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Follow.objects.count())

    def test_follow(self):
        self.assertFalse(Follow.objects.count())
        self.client.force_login(self.user_follower)

        # check hrefs exists
        response = self.client.get(
            rv("profile", kwargs={"username": "testuser_following"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'href="{rv("profile_follow", args=["testuser_following"])}"'
        )

        # follow
        response = self.client.get(
            rv(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                }
            )
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
                Follow.objects.get(
                        user=self.user_follower,
                        author=self.user_following
                )
        )

        # check hrefs exists
        response = self.client.get(
            rv("profile", kwargs={"username": "testuser_following"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'href="{rv("profile_unfollow", args=["testuser_following"])}"'
        )

    def following_author_posts_display(self):
        # check post not display
        self.client.force_login(self.user_follower)
        response = self.client.get(
            rv("follow_index")
        )

        self.assertNotContains(
            response,
            self.post.text
        )

        # follow
        self.client.get(
            rv(
                "profile_follow",
                kwargs={
                    "username": self.user_following.username,
                }
            )
        )

        # check post display
        response = self.client.get(
            rv("follow_index")
        )

        self.assertContains(
            response,
            self.post.text
        )
