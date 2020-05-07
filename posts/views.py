from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Comment, Follow
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect



def index(request):
    post_list = Post.objects.prefetch_related("author") \
                            .order_by("-pub_date") \
                            .all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "index.html",
                  {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.prefetch_related("author") \
                            .filter(group=group) \
                            .order_by("-pub_date")[:10]
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "group.html",
                  {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):

    # Create a next page param string
    next_url = request.GET.get("next")

    next_param = ""
    if next_url:
        next_param = "?next="+next_url

    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            return redirect(reverse("index"))

        return render(request, "new_post.html",
                      {"form": form, "mode": "add", "next_param": next_param})

    form = PostForm()
    return render(request, "new_post.html",
                  {"form": form, "mode": "add", "next_param": next_param})


def profile(request, username):
    author = get_object_or_404(User, username=username)

    post_list = Post.objects.prefetch_related("author") \
                            .filter(author=author) \
                            .order_by("-pub_date")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    profile = get_profile_data(request, author)

    return render(
            request, "profile.html",
            {
                "page": page,
                "paginator": paginator,
                "profile": profile,
            }
        )


def post_view(request, username, post_id, comment_form=False):
    author = get_object_or_404(User, username=username)

    post = get_object_or_404(Post, pk=post_id)

    if not comment_form:
        comment_form = CommentForm()
    comments = Comment.objects.filter(post=post)

    profile = get_profile_data(request, author)

    return render(
            request, "post.html",
            {
                "post": post,
                "profile": profile,
                "comment_form": comment_form,
                "comments": comments,
            }
        )


# generate author profile data for current user
def get_profile_data(request, author):
    # follow button state
    if not request.user.is_authenticated:
        follow_status = "not_authenticated"
    elif request.user == author:
        follow_status = "self"
    else:
        # show unfullow button if follow record exist
        follow_status = Follow.objects \
                              .filter(user=request.user, author=author) \
                              .exists()

    post_count = Post.objects.filter(author=author).count()

    profile = {
        "author": author,
        "followers": Follow.objects.filter(author=author).count(),
        "following": Follow.objects.filter(user=author).count(),
        "follow_status": follow_status,
        "post_count": post_count
    }
    return profile


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect(
            reverse("post",
                    kwargs={"username": username, "post_id": post_id}
                    )
                )

    post = get_object_or_404(Post, id=post_id)

    # Form a next page param string
    next_url = request.GET.get("next")
    next_param = ""
    if next_url:
        next_param = "?next="+next_url

    if request.method == "POST":
        form = PostForm(request.POST or None,
                        instance=post,
                        files=request.FILES or None)

        if form.is_valid():
            next_url = request.GET.get("next")
            form.save()
            if next_url:
                return redirect(next_url)

            return redirect(
                reverse(
                    "post",
                    kwargs={"username": username, "post_id": post_id}
                )
            )

        context = {
            "form": form,
            "mode": "edit",
            "next_param": next_param,
            "post": post
        }
        return render(request, "new_post.html", context)

    form = PostForm(instance=post)

    context = {
        "form": form,
        "mode": "edit",
        "next_param": next_param,
        "post": post
    }
    return render(request, "new_post.html", context)


@login_required
def add_comment(request, username, post_id):

    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST or None)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            return redirect(
                reverse(
                    "post",
                    kwargs={"username": username, "post_id": post_id}
                )
            )

        return redirect("post", username, post_id)


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user).values("author")
    post_list = Post.objects.filter(author__in=follows)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request, "follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)

    if request.user == following:
        return redirect("profile", username)

    try:
        Follow.objects.get(user=request.user, author=following)
    except Follow.DoesNotExist:
        Follow.objects.create(user=request.user, author=following)

    #return redirect("profile", username)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)

    try:
        Follow.objects.get(user=request.user, author=following).delete()
    except Follow.DoesNotExist:
        pass

    #return redirect("profile", username)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
