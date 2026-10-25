from django.test import TestCase


class DeploymentSmokeTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_editor_page_loads(self):
        response = self.client.get('/editor/')

        self.assertEqual(response.status_code, 200)

    def test_service_worker_is_available_at_site_root(self):
        response = self.client.get('/service-worker.js')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Service-Worker-Allowed'],
            '/',
        )

    def test_analysis_endpoint_rejects_invalid_json(self):
        response = self.client.post(
            '/api/analyze/',
            data='{',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
