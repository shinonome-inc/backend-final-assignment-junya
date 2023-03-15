from accounts.forms import User
from django.test import TestCase
from django.urls import reverse

from .models import Tweet


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        Tweet.objects.create(user=self.user, content="test tweet")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["object_list"], Tweet.objects.all())


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")
        self.url = reverse("tweets:create")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        test_tweet = {"title": "test", "content": "testtweet"}
        response = self.client.post(self.url, test_tweet)
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertTrue(Tweet.objects.filter(content=test_tweet["content"]).exists())

    def test_failure_post_with_empty_content(self):
        empty_tweet = {"title": "test", "content": ""}
        response = self.client.post(self.url, empty_tweet)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])
        self.assertFalse(Tweet.objects.exists())

    def test_failure_post_with_too_long_content(self):
        too_long_tweet = {"content": "n" * 101}
        response = self.client.post(self.url, too_long_tweet)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertIn(
            "この値は 100 文字以下でなければなりません( {} 文字になっています)。".format(len(too_long_tweet["content"])),
            form.errors["content"],
        )
        self.assertFalse(Tweet.objects.exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, title="test", content="testtweet")
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweet"], self.tweet)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.client.login(
            username="testuser",
            password="testpassword",
        )
        self.tweet = Tweet.objects.create(user=self.user, title="test", content="tweet")
        self.tweet2 = Tweet.objects.create(user=self.user2, title="test2", content="tweet2")
        self.url = reverse("tweets:delete", kwargs={"pk": self.tweet.pk})
        self.url2 = reverse("tweets:delete", kwargs={"pk": self.tweet2.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertEqual(Tweet.objects.filter(content="tweet").count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 3}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.count(), 2)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(self.url2)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.count(), 2)


class TestFavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_favorited_tweet(self):
        pass


class TestUnfavoriteView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_unfavorited_tweet(self):
        pass
