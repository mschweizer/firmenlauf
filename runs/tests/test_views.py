"""Tests for the views of the runs application."""
from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from runs.models import Participant, RunningEvent


class RunningEventListViewTest(TestCase):
    """Test case for the RunningEventListView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

        # Create events with different registration deadlines
        self.open_event = RunningEvent.objects.create(
            name="Open Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
        )

        self.closed_event = RunningEvent.objects.create(
            name="Closed Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.yesterday,
        )

        self.limited_event = RunningEvent.objects.create(
            name="Limited Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
            max_participants=2,
        )

    def test_view_url_exists_at_desired_location(self):
        """Test that the view URL exists at the desired location."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Test that the view URL is accessible by name."""
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "runs/event_list.html")

    def test_only_open_events_in_context(self):
        """Test that only events with open registration are in the context."""
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("events", response.context)

        # Check that only open events are in the context
        events = response.context["events"]
        self.assertEqual(len(events), 2)
        self.assertIn(self.open_event, events)
        self.assertIn(self.limited_event, events)
        self.assertNotIn(self.closed_event, events)

    def test_available_spots_in_context(self):
        """Test that available spots information is in the context."""
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)

        # Check that available spots information is in the context
        events = response.context["events"]
        for event in events:
            if event.max_participants:
                self.assertTrue(hasattr(event, "available_spots"))


class RunningEventDetailViewTest(TestCase):
    """Test case for the RunningEventDetailView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

        # Create an event with open registration
        self.event = RunningEvent.objects.create(
            name="Test Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
        )

        # Create an event with closed registration
        self.closed_event = RunningEvent.objects.create(
            name="Closed Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.yesterday,
        )

        # Create an event with limited spots
        self.limited_event = RunningEvent.objects.create(
            name="Limited Event",
            date=self.tomorrow,
            location="Test Location",
            description="Test Description",
            registration_deadline=self.tomorrow,
            max_participants=1,
        )

        # Create a participant for the limited event
        self.participant = Participant.objects.create(
            event=self.limited_event,
            name="Test Participant",
            department="Test Department",
            year_of_birth=2000,
            tshirt_size="M",
            email="test@example.com",
        )

    def test_view_url_exists_at_desired_location(self):
        """Test that the view URL exists at the desired location."""
        response = self.client.get(f"/event/{self.event.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """Test that the view URL is accessible by name."""
        response = self.client.get(reverse("event_detail", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(reverse("event_detail", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "runs/event_detail.html")

    def test_form_in_context(self):
        """Test that the registration form is in the context."""
        response = self.client.get(reverse("event_detail", args=[self.event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_registration_closed(self):
        """Test that registration is closed for events with past deadline."""
        response = self.client.get(reverse("event_detail", args=[self.closed_event.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.closed_event.is_registration_open())
        self.assertContains(response, "Registration for this event is currently closed")

    def test_successful_registration(self):
        """Test successful registration for an event."""
        response = self.client.post(
            reverse("event_detail", args=[self.event.pk]),
            {
                "name": "New Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "new@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

        # Check that the participant was created
        self.assertTrue(
            Participant.objects.filter(
                event=self.event,
                name="New Participant",
                department="Test Department",
                year_of_birth=2000,
                tshirt_size="M",
                email="new@example.com",
            ).exists()
        )

    def test_waiting_list(self):
        """Test that participants are placed on waiting list when event is full."""
        response = self.client.post(
            reverse("event_detail", args=[self.limited_event.pk]),
            {
                "name": "Waiting Participant",
                "department": "Test Department",
                "year_of_birth": 2001,
                "tshirt_size": "L",
                "email": "waiting@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

        # Check that the participant was created and placed on waiting list
        waiting_participant = Participant.objects.get(
            event=self.limited_event,
            name="Waiting Participant",
        )
        self.assertTrue(waiting_participant.on_waiting_list)

    def test_already_registered(self):
        """Test that participants cannot register twice for the same event."""
        # First registration
        self.client.post(
            reverse("event_detail", args=[self.event.pk]),
            {
                "name": "Duplicate Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "M",
                "email": "duplicate@example.com",
            },
        )

        # Second registration with same details
        response = self.client.post(
            reverse("event_detail", args=[self.event.pk]),
            {
                "name": "Duplicate Participant",
                "department": "Test Department",
                "year_of_birth": 2000,
                "tshirt_size": "L",  # Different t-shirt size
                "email": "different@example.com",  # Different email
            },
        )

        # Should redirect to already registered page
        self.assertEqual(response.status_code, 302)

        # Check that only one participant was created
        self.assertEqual(
            Participant.objects.filter(
                event=self.event,
                name="Duplicate Participant",
                department="Test Department",
                year_of_birth=2000,
            ).count(),
            1,
        )
