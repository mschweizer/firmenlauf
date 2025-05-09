"""Tests for the models of the runs application."""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from runs.models import Participant, RunningEvent


class RunningEventModelTest(TestCase):
    """Test case for the RunningEvent model."""

    def setUp(self):
        """Set up test data."""
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

        # Create a running event with registration deadline in the future
        self.open_event = RunningEvent.objects.create(
            name="Test Open Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
        )

        # Create a running event with registration deadline in the past
        self.closed_event = RunningEvent.objects.create(
            name="Test Closed Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.yesterday,
        )

        # Create a running event with max participants
        self.limited_event = RunningEvent.objects.create(
            name="Test Limited Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
            max_participants=2,
        )

    def test_string_representation(self):
        """Test the string representation of a RunningEvent."""
        self.assertEqual(str(self.open_event), "Test Open Event")

    def test_is_registration_open(self):
        """Test the is_registration_open method."""
        self.assertTrue(self.open_event.is_registration_open())
        self.assertFalse(self.closed_event.is_registration_open())

    def test_get_available_spots(self):
        """Test the get_available_spots method."""
        self.assertIsNone(self.open_event.get_available_spots())
        self.assertEqual(self.limited_event.get_available_spots(), 2)

        # Add a participant to the limited event
        Participant.objects.create(
            event=self.limited_event,
            name="Test Participant",
            department="Test Department",
            year_of_birth=2000,
            tshirt_size="M",
            email="test@example.com",
        )

        # Refresh from database
        self.limited_event.refresh_from_db()
        self.assertEqual(self.limited_event.get_available_spots(), 1)

    def test_has_available_spots(self):
        """Test the has_available_spots method."""
        self.assertTrue(self.open_event.has_available_spots())
        self.assertTrue(self.limited_event.has_available_spots())

        # Add two participants to the limited event
        Participant.objects.create(
            event=self.limited_event,
            name="Test Participant 1",
            department="Test Department",
            year_of_birth=2000,
            tshirt_size="M",
            email="test1@example.com",
        )
        Participant.objects.create(
            event=self.limited_event,
            name="Test Participant 2",
            department="Test Department",
            year_of_birth=2001,
            tshirt_size="L",
            email="test2@example.com",
        )

        # Refresh from database
        self.limited_event.refresh_from_db()
        self.assertFalse(self.limited_event.has_available_spots())


class ParticipantModelTest(TestCase):
    """Test case for the Participant model."""

    def setUp(self):
        """Set up test data."""
        self.event = RunningEvent.objects.create(
            name="Test Event",
            date=timezone.now().date() + timedelta(days=1),
            location="Test Location",
            description="Test Description",
        )

        self.participant = Participant.objects.create(
            event=self.event,
            name="Test Participant",
            department="Test Department",
            year_of_birth=2000,
            tshirt_size="M",
            email="test@example.com",
        )

    def test_string_representation(self):
        """Test the string representation of a Participant."""
        self.assertEqual(str(self.participant), "Test Participant - Test Event")

    def test_waiting_list(self):
        """Test the waiting list functionality."""
        self.assertFalse(self.participant.on_waiting_list)

        # Create a participant on the waiting list
        waiting_participant = Participant.objects.create(
            event=self.event,
            name="Waiting Participant",
            department="Test Department",
            year_of_birth=2001,
            tshirt_size="L",
            email="waiting@example.com",
            on_waiting_list=True,
        )

        self.assertTrue(waiting_participant.on_waiting_list)
