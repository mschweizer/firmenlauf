"""Views for the runs application."""
# Django imports
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

# Local application imports
from .forms import ParticipantForm
from .models import Participant, RunningEvent


class RunningEventListView(ListView):
    """
    View for displaying a list of running events with open registration.

    This view shows all running events where registration is still open,
    ordered by date. It also adds information about available spots for
    events with a maximum number of participants.
    """

    model = RunningEvent
    template_name = "runs/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        """
        Get the list of running events with open registration.

        Returns:
            list: A list of RunningEvent objects with open registration.
        """
        events = RunningEvent.objects.all().order_by("date")
        # Filter to only include events where registration is open
        return [event for event in events if event.is_registration_open()]

    def get_context_data(self, **kwargs):
        """
        Add available spots information to the context.

        Returns:
            dict: The context dictionary with added available spots information.
        """
        context = super().get_context_data(**kwargs)
        # Add available spots information to each event
        for event in context["events"]:
            if event.max_participants:
                event.available_spots = event.get_available_spots()
        return context


class RunningEventDetailView(DetailView):
    """
    View for displaying details of a running event and handling registration.

    This view shows the details of a running event and provides a registration form.
    It also handles the registration process, including checking if registration is open,
    if there are available spots, and if the participant is already registered.
    """

    model = RunningEvent
    template_name = "runs/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        """
        Add registration form and available spots information to the context.

        Returns:
            dict: The context dictionary with added form and available spots information.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = ParticipantForm(event=self.object)

        # Add available spots information
        if self.object.max_participants:
            context["available_spots"] = self.object.get_available_spots()

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for participant registration.

        This method processes the registration form, checks if registration is open,
        if there are available spots, and if the participant is already registered.

        Args:
            request: The HTTP request
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            HttpResponse: Redirect to success page, already registered page,
                or back to form with errors
        """
        self.object = self.get_object()

        # Check if registration is open
        if not self.object.is_registration_open():
            messages.error(request, "Registration for this event is closed.")
            return redirect("event_detail", pk=self.object.pk)

        form = ParticipantForm(request.POST, event=self.object)
        if form.is_valid():
            participant = form.save(commit=False)

            # Check if there are available spots
            if self.object.max_participants and not self.object.has_available_spots():
                participant.on_waiting_list = True
                messages.warning(
                    request, "No spots available. You have been placed on the waiting list."
                )

            participant.save()
            return redirect("registration_success", pk=participant.pk)
        else:
            # Check if this is our special "already registered" error
            if "already_registered" in form.errors[NON_FIELD_ERRORS]:
                # Redirect to the already registered page with the existing participant
                return redirect("already_registered", pk=form.existing_participant.pk)

        context = self.get_context_data(object=self.object)
        context["form"] = form
        return render(request, self.template_name, context)


class RegistrationSuccessView(DetailView):
    """
    View for displaying registration success information.

    This view shows the details of a successful registration, including
    participant information and event details. It also indicates if the
    participant has been placed on a waiting list.
    """

    model = Participant
    template_name = "runs/registration_success.html"
    context_object_name = "participant"


class AlreadyRegisteredView(DetailView):
    """
    View for displaying information when a participant is already registered.

    This view shows the details of an existing registration when a participant
    tries to register again for the same event. It includes the registration timestamp
    and admin contact information.
    """

    model = Participant
    template_name = "runs/already_registered.html"
    context_object_name = "participant"

    def get_context_data(self, **kwargs):
        """
        Add admin email to the context.

        Returns:
            dict: The context dictionary with added admin email.
        """
        context = super().get_context_data(**kwargs)
        context["admin_email"] = settings.ADMIN_EMAIL
        return context
