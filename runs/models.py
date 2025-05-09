"""Models for the runs application."""
from django.db import models
from django.utils import timezone


class RunningEvent(models.Model):
    """
    Model representing a running event.

    A running event has a name, date, location, description, and optional registration deadline
    and maximum number of participants.
    """

    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    registration_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Last day for registration. If not set, registration is always open.",
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of participants allowed. If not set, there is no limit.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the running event."""
        return self.name

    def is_registration_open(self):
        """
        Check if registration is open based on the deadline.

        Returns:
            bool: True if registration is open, False otherwise.
        """
        if self.registration_deadline:
            today = timezone.now().date()
            if today > self.registration_deadline:
                return False
        return True

    def get_available_spots(self):
        """
        Calculate the number of available spots.

        Returns:
            int or None: The number of available spots, or None if there is no limit.
        """
        if not self.max_participants:
            return None  # No limit

        registered_count = self.participants.filter(on_waiting_list=False).count()
        return max(0, self.max_participants - registered_count)

    def has_available_spots(self):
        """
        Check if there are available spots.

        Returns:
            bool: True if there are available spots, False otherwise.
        """
        if not self.max_participants:
            return True  # No limit

        return self.get_available_spots() > 0

class Participant(models.Model):
    """
    Model representing a participant in a running event.

    A participant has a name, department, year of birth, t-shirt size, and email.
    They can be placed on a waiting list if the event is full.
    """

    TSHIRT_SIZES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
        ('NO', 'I already have a t-shirt'),
    ]

    event = models.ForeignKey(
        RunningEvent, 
        on_delete=models.CASCADE, 
        related_name='participants'
    )
    name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    year_of_birth = models.IntegerField()
    tshirt_size = models.CharField(max_length=3, choices=TSHIRT_SIZES)
    email = models.EmailField()
    on_waiting_list = models.BooleanField(
        default=False, 
        help_text="Indicates if the participant is on the waiting list"
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the participant."""
        return f"{self.name} - {self.event.name}"
