from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from accounts.forms import User
from accounts.models import FriendShip
from tweets.models import Tweet


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, data=data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            User.objects.filter(username="testuser", email="test@example.com").count(),
            1,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        empty_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, empty_data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(User.objects.count(), 0)

        form = response.context["form"]

        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_username(self):
        empty_data = {
            "username": "",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, empty_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])

        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_email(self):
        empty_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, empty_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_empty_password(self):
        empty_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, empty_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_duplicated_user(self):
        duplicated_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        response = self.client.post(self.url, duplicated_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

        self.assertEqual(User.objects.count(), 1)

    def test_failure_post_with_invalid_email(self):
        email_failure_data = {
            "username": "testuser",
            "email": "test_email",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, email_failure_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_too_short_password(self):
        password_failure_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "short",
            "password2": "short",
        }

        response = self.client.post(self.url, password_failure_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。"])
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_password_similar_to_username(self):
        password_failure_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testuser",
            "password2": "testuser",
        }

        response = self.client.post(self.url, password_failure_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_only_numbers_password(self):
        password_failure_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "16475843",
            "password2": "16475843",
        }

        response = self.client.post(self.url, password_failure_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["このパスワードは数字しか使われていません。"])
        self.assertEqual(User.objects.count(), 0)

    def test_failure_post_with_mismatch_password(self):
        password_failure_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword1",
        }

        response = self.client.post(self.url, password_failure_data)
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])
        self.assertEqual(User.objects.count(), 0)


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        data = {
            "username": "test2",
            "password": "testpassword",
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            ["正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        empty_data = {
            "username": "test2",
            "password": "",
        }
        response = self.client.post(self.url, empty_data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["このフィールドは必須です。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.url = reverse("accounts:user_profile", args=[self.user1.username])
        self.client.force_login(self.user1)
        FriendShip.objects.create(following=self.user2, follower=self.user1)

    def test_success_get(self):
        Tweet.objects.create(user=self.user1, content="testcontent")
        Tweet.objects.create(user=self.user2, content="testcontent")
        response = self.client.get(self.url)

        self.assertQuerysetEqual(response.context["object_list"], Tweet.objects.filter(user=self.user1))

        self.assertEqual(response.context["following_count"], FriendShip.objects.filter(follower=self.user1).count())
        self.assertEqual(response.context["follower_count"], FriendShip.objects.filter(following=self.user1).count())


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        self.client.login(username="testuser1", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "testuser2"}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 1)

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "user3"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")
        FriendShip.objects.create(following=self.user2, follower=self.user1)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "testuser2"}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "user3"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 1)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FriendShip.objects.filter(follower=self.user1).count(), 1)


class TestFollowingListView(TestCase):
    def test_success_get(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.friendship1 = FriendShip.objects.create(following=self.user2, follower=self.user1)
        self.friendship2 = FriendShip.objects.create(following=self.user1, follower=self.user2)
        self.client.login(username="testuser1", password="testpassword")
        response = self.client.get(reverse("accounts:following_list", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["following_list"]), 1)
        self.assertEqual(response.context["following_list"][0], self.friendship1)


class TestFollowerListView(TestCase):
    def test_success_get(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.friendship1 = FriendShip.objects.create(following=self.user2, follower=self.user1)
        self.friendship2 = FriendShip.objects.create(following=self.user1, follower=self.user2)
        self.client.login(username="testuser1", password="testpassword")
        response = self.client.get(reverse("accounts:follower_list", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["follower_list"]), 1)
        self.assertEqual(response.context["follower_list"][0], self.friendship2)
