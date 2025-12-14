from django.conf import settings
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    # Indexed + unique helps lookups like Tag.objects.get(name=...)
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="projects")
    link = models.URLField(max_length=200, blank=True)

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
    """
    Simple viewer profile tied to Django's auth User.
    - Gives a place to store display info for commenters.
    - A Profile can be auto-created on user signup via a post_save signal (optional).
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=120, blank=True)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.display_name or self.user.get_username()


class Comment(models.Model):
    """
    User comments on a Project.
    """

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
    content = models.TextField()

    # ✅ Index for ordering/filtering at scale
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # ✅ Helpful when you frequently query "comments for a project, newest first"
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
