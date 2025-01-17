import json
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.test import Client, TestCase

from common.models import BaseModel


def create_basic_controller_test(model: type[BaseModel], url: str):  # noqa: C901
    """Create a basic controller test for a model."""

    def create_test_object(fields: list[models.Field]) -> dict:
        """Create a test object for a model."""
        test_data = {}

        for field in fields:
            match type(field):
                case models.CharField:
                    test_data[field.name] = "test"
                case models.TextField:
                    test_data[field.name] = "test"
                case models.IntegerField:
                    test_data[field.name] = 1
                case models.BooleanField:
                    test_data[field.name] = True
                case models.DateField:
                    test_data[field.name] = datetime.now(tz=settings.TIME_ZONE).date()
                case models.DecimalField:
                    test_data[field.name] = 1.0

        return test_data

    def create_update_fields(fields: list[models.Field]) -> dict:
        """Create update fields for a model."""
        update_fields = {}

        for field in fields:
            match type(field):
                case models.CharField:
                    update_fields[field.name] = "upload"
                case models.TextField:
                    update_fields[field.name] = "upload"
                case models.IntegerField:
                    update_fields[field.name] = 0
                case models.BooleanField:
                    update_fields[field.name] = False
                case models.DateField:
                    update_fields[field.name] = datetime.now(tz=settings.TIME_ZONE).date() + timedelta(days=1)
                case models.DecimalField:
                    update_fields[field.name] = 2.00

        return update_fields

    class ControllerTest(TestCase):
        def setUp(self) -> None:
            self.url = f"/api/{url}"
            client = Client()
            response = client.post(
                "/api/auth/obtain",
                data=json.dumps({"email": settings.TEST_ACCOUNT_EMAIL, "password": settings.TEST_ACCOUNT_PASSWORD}),
                content_type="application/json",
            )
            jwt = response.json().get("access")
            self.client = Client(headers={"Authorization": f"Bearer {jwt}"})
            self.fields = model._meta.get_fields()[9:]
            self.instance = model.objects.get()

        @classmethod
        def setUpTestData(cls) -> None:
            user = models.User.objects.create_user(  # type: ignore
                username="test_account",
                email=settings.TEST_ACCOUNT_EMAIL,
                password=settings.TEST_ACCOUNT_PASSWORD,
            )
            fields = model._meta.get_fields()[9:]
            instance = model(**create_test_object(fields))  # type: ignore
            instance.save(user)

        def test_get(self) -> None:
            get_id = model.objects.get().id
            response = self.client.get(self.url + f"/{get_id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json().get("id"), str(get_id))

        def test_get_all(self) -> None:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 1)

        def test_create(self) -> None:
            data = create_test_object(self.fields)  # type: ignore
            response = self.client.post(self.url, data, "application/json")
            self.assertEqual(response.status_code, 200)
            for field_name, field_value in data.items():
                self.assertEqual(str(response.json().get(field_name)), str(field_value))

        def test_update(self) -> None:
            update_data = create_update_fields(self.fields)  # type: ignore
            response = self.client.put(f"{self.url}/{self.instance.id}", update_data, "application/json")

            self.assertEqual(response.status_code, 200)

            self.instance.refresh_from_db()
            for field_name, update_value in update_data.items():
                current_value = getattr(self.instance, field_name)
                if isinstance(current_value, float) or isinstance(update_value, float):
                    self.assertEqual(float(current_value), float(update_value))
                else:
                    self.assertEqual(str(current_value), str(update_value))

        def test_delete(self) -> None:
            response = self.client.delete(f"{self.url}/{self.instance.id}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(model.objects.count(), 0)

    return ControllerTest
