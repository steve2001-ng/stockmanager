import re
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

MENTION_RE = re.compile(r'@(?P<username>[\w.@+-]+)')

class Message(models.Model):
    author     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    subject    = models.CharField(max_length=255)
    body       = models.TextField()
    mentions   = models.ManyToManyField(
        User,
        related_name='mentioned_in_messages',
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    read_by    = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_messages',
        blank=True,
        help_text="Les utilisateurs ayant déjà lu ce message"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} par {self.author}"

    def save(self, *args, **kwargs):
        # Sauvegarde initiale pour avoir l'ID
        super().save(*args, **kwargs)

        # Recherche tous les @username dans le body
        found = set(MENTION_RE.findall(self.body))
        if found:
            # Récupère les utilisateurs correspondants
            users = User.objects.filter(username__in=found)
            # Met à jour la relation many-to-many
            self.mentions.set(users)
        else:
            # Vide la relation s’il n’y a plus de mentions
            self.mentions.clear()

class Comment(models.Model):
    message    = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body       = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.message.id}"
