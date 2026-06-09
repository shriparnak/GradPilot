from django.shortcuts import render, redirect
from .models import Profile,Task

def home(request):
    return render(request, 'home.html')

def login_view(request):
    error = None

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = Profile.objects.filter(
            email=email,
            password=password
        ).first()

        if user:
            request.session['user_id'] = user.id

            if not user.profile_completed:
                return redirect('/profile/')

            return redirect('/dashboard/')

        else:
            error = "Invalid email or password"

    return render(request, 'login.html', {'error': error})

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        password = request.POST['password']

        # Check if email already exists
        if Profile.objects.filter(email=email).exists():
            return render(request, 'signup.html', {
                'error': 'Email already exists. Try another one.'
            })

        # Create user
        user = Profile.objects.create(
            full_name=full_name,
            email=email,
            password=password
        )

        # Auto login after signup
        request.session['user_id'] = user.id

        # Go directly to profile setup
        return redirect('/profile/')

    return render(request, 'signup.html')


def dashboard(request):

    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('/login/')

    user = Profile.objects.get(id=user_id)
    section = request.GET.get(
        'section',
        'Weekly Goals'
    )

    # get all tasks
    tasks = Task.objects.filter(
    user=user,
    category=section
    )

    # convert tasks into textarea format
    saved_goals = "\n".join(
        [task.task_text for task in tasks]
    )

    # =========================
    # HANDLE POST REQUESTS
    # =========================

    if request.method == "POST":

        # =========================
        # SAVE / EDIT GOALS
        # =========================

        goals = request.POST.get("weekly_goals")

        if goals is not None:

            old_tasks = Task.objects.filter(
                user=user,
                category=section
            )

            # preserve checkbox states
            completed_tasks = {}

            for task in old_tasks:

                completed_tasks[
                    task.task_text.strip()
                ] = task.is_completed

            # delete old tasks
            old_tasks.delete()

            # split textarea into lines
            goal_list = goals.splitlines()

            # recreate tasks
            for goal in goal_list:

                cleaned_goal = goal.strip()

                if cleaned_goal:

                    Task.objects.create(
                        user=user,
                        task_text=cleaned_goal,
                        category=section,
                        is_completed=completed_tasks.get(
                            cleaned_goal,
                            False
                        )
                    )

            return redirect(f'/dashboard/?section={section}')

        # =========================
        # SAVE CHECKBOX PROGRESS
        # =========================

        completed_task_ids = request.POST.getlist(
            "completed_tasks"
        )

        # reset all tasks in current section
        tasks.update(is_completed=False)

        # get checked tasks
        checked_tasks = Task.objects.filter(
            user=user,
            id__in=completed_task_ids
        )

        # sync completion across all sections
        for task in checked_tasks:

            Task.objects.filter(
                user=user,
                task_text=task.task_text
            ).update(is_completed=True)

        return redirect(f'/dashboard/?section={section}')

    # =========================
    # REFRESH TASKS
    # =========================

    tasks = Task.objects.filter(
        user=user,
        category=section
    )

    saved_goals = "\n".join(
        [task.task_text for task in tasks]
    )

    # =========================
    # PROGRESS LOGIC
    # =========================

    total_tasks = tasks.count()

    completed_tasks = tasks.filter(
        is_completed=True
    ).count()

    progress = 0

    if total_tasks > 0:

        progress = int(
            (completed_tasks / total_tasks) * 100
        )

    # =========================
    # RENDER PAGE
    # =========================

    

    all_tasks = Task.objects.filter(
    user=user
).exclude(
    category="Weekly Goals"
)

    overall_total = all_tasks.count()

    overall_completed = all_tasks.filter(
        is_completed=True
    ).count()

    overall_progress = 0

    if overall_total > 0:
        overall_progress = int(
            (overall_completed / overall_total) * 100
        )
    return render(request, 'dashboard.html', {

        'request': request,
        'user': user,
        'section': section,
        'saved_goals': saved_goals,
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress': progress,
        'overall_progress': overall_progress,

    })

def profile(request):
    user_id = request.session.get('user_id')
    user = Profile.objects.get(id=user_id)

    if request.method == 'POST':

        new_role = request.POST['target_role']

        # only reset if role actually changed
        if user.target_role != new_role:

            Task.objects.filter(
                user=user
            ).delete()

        user.target_role = new_role
        user.profile_completed = True
        user.save()

        return redirect('/dashboard/')

    return render(request, 'profile.html')

def logout_view(request):
    request.session.flush()   # clears user session
    return redirect('/login/')
