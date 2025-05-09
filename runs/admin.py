"""Admin configuration for the runs application."""

from django.contrib import admin

from .models import Participant, RunningEvent


class ParticipantInline(admin.TabularInline):
    """Inline admin for participants to be included in the running event admin."""

    model = Participant
    extra = 0
    readonly_fields = ("registered_at",)


@admin.register(RunningEvent)
class RunningEventAdmin(admin.ModelAdmin):
    """Admin configuration for the RunningEvent model."""

    list_display = (
        "name",
        "date",
        "location",
        "registration_deadline",
        "max_participants",
        "created_at",
    )
    list_filter = ("date", "registration_deadline")
    search_fields = ("name", "location")
    inlines = [ParticipantInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """Admin configuration for the Participant model."""

    list_display = (
        "name",
        "event",
        "department",
        "year_of_birth",
        "tshirt_size",
        "email",
        "on_waiting_list",
        "registered_at",
    )
    list_filter = ("event", "tshirt_size", "department", "on_waiting_list")
    search_fields = ("name", "email")
    readonly_fields = ("registered_at",)
