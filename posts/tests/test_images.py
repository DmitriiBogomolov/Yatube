from django.test import TestCase, Client
from posts.models import Post, Group
from django.contrib.auth.models import User
from django.shortcuts import reverse as rv
from django.core.cache import cache

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from zipfile import ZipFile

import os, glob
from django.conf import settings


# clear uploaded files in previous tests
def _set_up():
    files = glob.glob(
        os.path.join(settings.MEDIA_ROOT+"\\posts\\"+"test_image*")
    )
    for filename in files:
        os.remove(filename)

    files = glob.glob(
        os.path.join(settings.MEDIA_ROOT+"\\posts\\"+"another_test_image*")
    )
    for filename in files:
        os.remove(filename)


_set_up()


class TestImages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        username="testuser",
                        email="testuser@yandex.ru",
                        password="12345",
                        first_name="Dmitrii",
                        last_name="Bogomolov"
        )
        self.client.force_login(self.user)

        self.group = Group.objects.create(
                        title="testgroup",
                        slug="testgroup"
                    )

        # generate random image file
        img = Image.new("RGB", (200, 100), color="red")
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        self.img_file = InMemoryUploadedFile(
                            img_io,
                            None,
                            "test_image.jpg",
                            "image/jpeg",
                            None, None
                        )

        self.post = Post.objects.create(
                        text="testpost",
                        author=self.user,
                        image=self.img_file,
                        group=self.group
                    )

        # generate random .zip file
        zip_io = BytesIO()
        zip_raw = ZipFile(zip_io, "w")
        zip_raw.close()
        self.zip_file = InMemoryUploadedFile(
                            zip_io,
                            None,
                            "zip_file.zip",
                            "application/zip",
                            None, None
                        )


    def test_post_image_display(self):
        response = self.client.get(
                    rv(
                        "post",
                        kwargs={
                            "username": "testuser",
                            "post_id": self.post.id
                        }
                    )
        )

        self.assertContains(response, "<img")

    def test_profile_post_image_display(self):
        response = self.client.get(
                        rv(
                            "profile",
                            kwargs={"username": "testuser"}
                        )
        )
        self.assertContains(response, "<img")

    def test_group_post_image_display(self):
        response = self.client.get(
                        rv(
                            "group_posts",
                            kwargs={"slug": "testgroup"}
                        )
        )
        self.assertContains(response, "<img")

    def test_index_post_image_display(self):
        cache.clear()
        response = self.client.get(rv("index"))
        self.assertContains(response, "<img")

    def test_wrong_img_file_upload(self):
        # generate another random image file
        img = Image.new("RGB", (300, 200), color="blue")
        img_io = BytesIO()
        img.save(img_io, format="JPEG")
        another_img_file = InMemoryUploadedFile(
                                img_io,
                                None,
                                "another_test_image.jpg",
                                "image/jpeg",
                                None, None
                            )

        # test new post image
        response = self.client.post(
                        rv("new_post"),
                        {
                            "text": "testpost1111",
                            "image": self.img_file.open()
                        }
                    )
        self.assertEqual(response.status_code, 302)

        post = Post.objects.get(text="testpost1111")
        self.assertEqual(post.image.read(), self.img_file.file.getvalue())

        # test post edit image
        response = self.client.post(
                        rv(
                            "post_edit",
                            kwargs={
                                "username": "testuser",
                                "post_id": post.id
                            }
                        ),
                        {
                            "text": "testpost22222",
                            "image": another_img_file.open()
                        }
                    )
        post = Post.objects.get(id=post.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.image.read(), another_img_file.file.getvalue())

        # test edit wrong post image
        response = self.client.post(
                        rv(
                            "post_edit",
                            kwargs={
                                "username": "testuser",
                                "post_id": post.id
                            }
                        ),
                        {
                            "text": "testpost22222",
                            "image": self.zip_file.open()
                        }
                    )
        post = Post.objects.get(id=post.id)

        self.assertEqual(post.image.read(), another_img_file.file.getvalue())

        # test new wrong post image
        response = self.client.post(
                        rv("new_post"),
                        {
                            "text": "wrong_post_image_post",
                            "image": self.zip_file.open()
                        }
                    )
        self.assertRaises(
                Post.DoesNotExist,
                Post.objects.get,
                text="wrong_post_image_post"
        )