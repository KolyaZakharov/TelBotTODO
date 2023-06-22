from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    is_complete = models.BooleanField()

    class Meta:
        ordering = ["is_complete", "-due_date"]

    def __str__(self):
        return self.title
