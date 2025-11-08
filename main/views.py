from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from .models import Project, Tag, Comment
from .forms import CommentForm, ContactForm

from datetime import datetime

# Create views here.

def home(request):
    projects = Project.objects.all()  # Gives access to all projects on the home page.
    tags = Tag.objects.all()
    # Rendering just means to show on the screen.
    return render(request, "index.html", {"projects": projects, "tags": tags})


def contact(request):
    """
    Handle contact form submissions and render the contact page.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message_text = request.POST.get("message", "").strip()

        # Form data can be processed here if needed 

        messages.success(request, "Message received. A response will be sent if required.")
        return redirect("contact")

    return render(request, "contact.html")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Access validated data safely
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message_text = form.cleaned_data["message"]

            # TODO: handle the form (send email, save to DB, etc.)

            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")  
        else:
            # Form is invalid: fall through and re-render with errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


def about(request):
    return render(request, "about.html")


def project(request, id):
    # Look for the pk specified, within the project model.
    project_obj = get_object_or_404(Project, pk=id)

    # ADDED: list comments and show empty form
    comments = project_obj.comments.select_related("user").all()

    # allow either Django-auth or sheet-auth to post
    can_comment = request.user.is_authenticated or bool(
        request.session.get("user_email")
    )
    form = CommentForm() if can_comment else None

    return render(
        request,
        "project.html",
        {
            "project": project_obj,
            "comments": comments,
            "form": form,  # used for the "create comment" form
        },
    )


# partial view so the home page modal can load comments for a single project
def project_comments_partial(request, id):
    """
    Render just the comments + (optional) form for a specific project.
    Used by the home page popup.
    """
    project_obj = get_object_or_404(Project, pk=id)
    comments = project_obj.comments.select_related("user").order_by("-created_at")

    # if logged in via Django OR via sheet, show form
    can_comment = request.user.is_authenticated or bool(
        request.session.get("user_email")
    )
    form = CommentForm() if can_comment else None

    return render(
        request,
        "partials/project_comments.html",
        {
            "project": project_obj,
            "comments": comments,
            "form": form,
        },
    )


# Below is the ability to add comments to satisfy CRUD.

@require_POST
def comment_create(request, id):
    """
    Create a new comment on a project.
    only accepts:
    - Django authenticated users
    - Sheet/session users (email + name stored in session)
    """
    project_obj = get_object_or_404(Project, pk=id)

    # detect auth method
    is_django_user = request.user.is_authenticated
    sheet_email = request.session.get("user_email")
    sheet_name = request.session.get("user_name")
    session_author_name = request.session.get("author_name")

    # consider any of these as valid sheet/session identity
    has_sheet_identity = bool(sheet_email or sheet_name or session_author_name)

    # block if neither is present
    if not is_django_user and not has_sheet_identity:
        messages.error(request, "Sign in is required to comment.")
        return redirect(reverse("project", kwargs={"id": project_obj.pk}))

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.project = project_obj

        if is_django_user:
            # normal Django user FK
            comment.user = request.user
        else:
            # sheet/session path — model must have author_name for this to work
            comment.author_name = sheet_name or session_author_name or sheet_email

        comment.save()
        messages.success(request, "Comment posted.")
    else:
        messages.error(request, "Please fix the errors and try again.")

    return redirect(reverse("project", kwargs={"id": project_obj.pk}))


@login_required
def comment_update(request, id, comment_id):
    """
    Update an existing comment (only by its owner).
    """
    project_obj = get_object_or_404(Project, pk=id)
    comment = get_object_or_404(
        Comment, pk=comment_id, project=project_obj, user=request.user
    )

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
        else:
            messages.error(request, "Please fix the errors and try again.")

    return re

@login_required
@require_POST
def comment_delete(request, id, comment_id):
    """
    Delete a comment (only by its owner).
    """
    project_obj = get_object_or_404(Project, pk=id)
    comment = get_object_or_404(
        Comment, pk=comment_id, project=project_obj, user=request.user
    )

    comment.delete()
    messages.success(request, "Comment deleted.")

    return redirect(reverse("project", kwargs={"id": project_obj.pk}))
