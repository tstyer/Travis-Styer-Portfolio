from django.conf import settings
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="projects")

    # Optional live/demo link (or general link)
    link = models.URLField(max_length=200, blank=True)

    # NEW: Optional GitHub repo link for your modal CTA
    github_url = models.URLField(max_length=300, blank=True)

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="project_images/")

    def __str__(self):
        return f"{self.project.title} Image"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120, blank=True)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.display_name or self.user.get_username()


class Comment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )

    author_name = models.CharField(max_length=120, blank=True)

    # NEW: more reliable ownership match for session/sheet users
    author_email = models.EmailField(blank=True)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "-created_at"]),
        ]

    def __str__(self):
        who = self.user if self.user else (self.author_name or "Anon")
        return f"Comment by {who} on {self.project}"


# *Self-learn note:
# To create a model, include `models.Model` in parentheses so the class
# defines a Django model. Then add fields via dot-notation: e.g. `title`,
# `TextField`, etc.
