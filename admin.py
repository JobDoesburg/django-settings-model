from django.contrib import admin
from constants import models
from constants.constants import constants


@admin.register(models.Constant)
class ConstantAdmin(admin.ModelAdmin):
    """Constant Admin."""

    model = models.Constant

    list_display = ["slug", "value", "type", "nullable", "in_use"]
    fields = ["slug", "value", "type", "nullable", "in_use"]
    readonly_fields = ["slug", "type", "nullable", "in_use"]

    def in_use(self, obj):
        """Get in use."""
        return constants.is_registered(obj.slug)

    in_use.boolean = True

    def has_delete_permission(self, request, obj=None):
        """Get delete permission."""
        return obj is None or not constants.is_registered(obj.slug)
