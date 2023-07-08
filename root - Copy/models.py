from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import os

# from django.db.models.signals import pre_delete
# from django.dispatch import receiver
# import os

# def delete_file(instance, **kwargs):
#     if instance.file:
#         if os.path.isfile(instance.file.path):
#             os.remove(instance.file.path)

# @receiver(pre_delete, sender=User)
# def delete_files(sender, instance, **kwargs):
#     for blog_post in instance.blogpost_set.all():
#         delete_file(blog_post)

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    

class AllFiles(models.Model):
    owner= models.ForeignKey(User, on_delete=models.CASCADE)
    title= models.CharField(max_length=100)
    file=models.FileField(upload_to='all_files/', default='')
    created_at=models.DateTimeField(auto_now_add=True,)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})
    
    def delete(self, *args, **kwargs):
        if self.file:
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def filename(self):
        return os.path.basename(self.file.name)

