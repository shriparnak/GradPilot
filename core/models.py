from django.db import models

class Profile(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    target_role = models.CharField(max_length=50, blank=True)
    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
class Task(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    category = models.CharField(
        max_length=50,
        default="Weekly Goals"
    )

    task_text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task_text