from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .models import CustomUser, UserLoginAttempt

class SigninViewTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.signin_url = reverse('signin')

    def test_successful_login(self):
        response = self.client.post(reverse('signin'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login_incorrect_password(self):
        response = self.client.post(reverse('signin'), {
            'email': 'test@example.com',
            'password': 'Hajer123.'  # Incorrect password
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mot de passe incorrect. Veuillez réessayer.")

    def test_failed_login_nonexistent_user(self):
        response = self.client.post(reverse('signin'), {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Aucun utilisateur trouvé", response.content.decode('utf-8'))
        self.assertContains(response, "Aucun utilisateur trouvé avec l&#x27;email nonexistent@example.com")

    @patch('accounts.views.notify_user')
    def test_anomaly_detection(self, mock_notify):
        # Simulate 3 failed login attempts
        for _ in range(3):
            response = self.client.post(reverse('signin'), {
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })

        self.assertEqual(mock_notify.call_count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Trop de tentatives de connexion infructueuses. Veuillez réessayer plus tard.", response.content.decode('utf-8'))
        mock_notify.assert_called_once_with('test@example.com')
        self.assertEqual(UserLoginAttempt.objects.filter(user=self.user).count(), 3)


