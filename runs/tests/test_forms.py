"""Tests for the forms of the runs application."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from runs.forms import ParticipantForm
from runs.models import Participant, RunningEvent


class ParticipantFormTest(TestCase):
    """Test case for the ParticipantForm."""

    def setUp(self):
        """Set up test data."""
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)

        # Create a running event
        self.event = RunningEvent.objects.create(
            name="Test Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
        )

        # Create a participant for the event
        self.participant = Participant.objects.create(
            event=self.event,
            name="Existing Participant",
            department="Test Department",
            year_of_birth=2000,
            tshirt_size="M",
            email="existing@example.com",
        )

    def test_form_valid_data(self):
        """Test form with valid data."""
        form = ParticipantForm(
            data={
                "name": "New Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "new@example.com",
            },
            event=self.event,
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """Test form with invalid data."""
        # Missing required fields
        form = ParticipantForm(
            data={
                "name": "",  # Empty name
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "new@example.com",
            },
            event=self.event,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

        # Invalid email
        form = ParticipantForm(
            data={
                "name": "New Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "not-an-email",  # Invalid email
            },
            event=self.event,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

        # Invalid year of birth (too old)
        form = ParticipantForm(
            data={
                "name": "New Participant",
                "department": "Test Department",
                "year_of_birth": 1800,  # Too old
                "tshirt_size": "M",
                "email": "new@example.com",
            },
            event=self.event,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("year_of_birth", form.errors)

    def test_form_already_registered(self):
        """Test form with already registered participant."""
        form = ParticipantForm(
            data={
                "name": "Existing Participant",  # Same name
                "department": "Test Department",  # Same department
                "year_of_birth": 2000,  # Same year of birth
                "tshirt_size": "L",  # Different t-shirt size
                "email": "different@example.com",  # Different email
            },
            event=self.event,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("already_registered", form.errors.get("__all__", []))
        self.assertTrue(hasattr(form, "existing_participant"))
        self.assertEqual(form.existing_participant, self.participant)

    def test_form_save(self):
        """Test form save method."""
        form = ParticipantForm(
            data={
                "name": "New Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "new@example.com",
            },
            event=self.event,
        )
        self.assertTrue(form.is_valid())

        # Save the form
        participant = form.save()

        # Check that the participant was created with the correct event
        self.assertEqual(participant.event, self.event)
        self.assertEqual(participant.name, "New Participant")
        self.assertEqual(participant.department, "Test Department")
        self.assertEqual(participant.year_of_birth, 2000)
        self.assertEqual(participant.tshirt_size, "M")
        self.assertEqual(participant.email, "new@example.com")
        self.assertFalse(participant.on_waiting_list)
