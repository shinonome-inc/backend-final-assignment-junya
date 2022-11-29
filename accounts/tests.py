from django.test import TestCase
from django.urls import reverse_lazy

from accounts.forms import SignupForm, User
from mysite.settings import LOGIN_REDIRECT_URL


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse_lazy("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        test_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, test_data)
        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse_lazy(LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
            msg_prefix="",
            fetch_redirect_response=True,
        )

        self.assertTrue(
            User.objects.filter(
                username=test_data["username"],
                email=test_data["email"],
            ).exists()
        )

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

        form = SignupForm(data=empty_data)

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

        form = SignupForm(data=empty_data)

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

        form = SignupForm(data=empty_data)

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

        form = SignupForm(data=empty_data)

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

        form = SignupForm(data=duplicated_data)
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

        form = SignupForm(data=email_failure_data)
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

        form = SignupForm(data=password_failure_data)
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

        form = SignupForm(data=password_failure_data)
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

        form = SignupForm(data=password_failure_data)
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

        form = SignupForm(data=password_failure_data)
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])
        self.assertEqual(User.objects.count(), 0)


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse_lazy("accounts:home")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestLoginView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_empty_password(self):
        pass


class TestLogoutView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


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
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_user(self):
        pass

    def test_failure_post_with_self(self):
        pass


class TestUnfollowView(TestCase):
    def test_success_post(self):
        pass

    def test_failure_post_with_not_exist_tweet(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowingListView(TestCase):
    def test_success_get(self):
        pass


class TestFollowerListView(TestCase):
    def test_success_get(self):
        pass
