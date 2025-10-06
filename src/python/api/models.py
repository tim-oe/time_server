from django.db import models


class TimeEntry(models.Model):
    """Model for storing time entries."""

    description = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Time Entry"
        verbose_name_plural = "Time Entries"

    def __str__(self):
        return f"{self.description} - {self.start_time}"

    def save(self, *args, **kwargs):
        """Calculate duration when saving."""
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)
