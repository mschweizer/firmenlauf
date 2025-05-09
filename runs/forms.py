"""Forms for the runs application."""

# Standard library imports

# Django imports
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _

# Local application imports
from .models import Participant


class ParticipantForm(forms.ModelForm):
    """
    Form for participant registration.

    This form collects participant information for registration to a running event.
    It validates that the participant is not already registered for the event.
    """

    class Meta:
        """Meta class for ParticipantForm."""

        model = Participant
        fields = ["name", "department", "year_of_birth", "tshirt_size", "email"]
        labels = {
            "name": _("Full Name"),
            "department": _("Department"),
            "year_of_birth": _("Year of Birth"),
            "tshirt_size": _("T-Shirt Size"),
            "email": _("Email"),
        }

        widgets = {
            "year_of_birth": forms.NumberInput(attrs={"min": 1900, "max": 2023}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments, including 'event'
        """
        self.event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)

    def clean_year_of_birth(self):
        """
        Validate the year_of_birth field.

        This method checks if the year of birth is within a reasonable range.

        Returns:
            int: The cleaned year of birth
        """
        year_of_birth = self.cleaned_data.get("year_of_birth")
        if year_of_birth and (year_of_birth < 1900 or year_of_birth > 2023):
            raise forms.ValidationError(_("Year of birth must be between 1900 and 2023."))
        return year_of_birth

    def clean(self):
        """
        Clean and validate the form data.

        This method checks if the participant is already registered for the event
        based on name, department, and year of birth.

        Returns:
            dict: The cleaned form data
        """
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        department = cleaned_data.get("department")
        year_of_birth = cleaned_data.get("year_of_birth")

        # Check if this person is already registered for this event
        if name and department and year_of_birth and self.event:
            try:
                self.existing_participant = Participant.objects.get(
                    event=self.event, name=name, department=department, year_of_birth=year_of_birth
                )
                # Instead of raising an error, we'll store the existing participant
                # and handle it in the view
                self.add_error(NON_FIELD_ERRORS, "already_registered")
            except Participant.DoesNotExist:
                pass

        return cleaned_data

    def save(self, commit=True):
        """
        Save the form data to create a new participant.

        This method associates the participant with the event before saving.

        Args:
            commit (bool): Whether to save the participant to the database

        Returns:
            Participant: The created participant object
        """
        participant = super().save(commit=False)
        participant.event = self.event
        if commit:
            participant.save()
        return participant
