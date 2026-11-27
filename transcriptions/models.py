from django.db import models

class Transcription(models.Model):
    title = models.CharField(max_length=200, default="Untitled transcription")
    text = models.TextField()
    language = models.CharField(max_length=50, blank=True, default="Unknown")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
