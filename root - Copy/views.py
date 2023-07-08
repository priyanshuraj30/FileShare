from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (CreateView,DeleteView,TemplateView)
from .models import AllFiles,Folder
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from .forms import FolderForm, FolderUploadForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse,HttpResponse,HttpResponseRedirect
import os,io
import zipfile
from django.utils.text import slugify



@login_required
def create_folder(request, parent_folder_id=None):
    parent_folder=None
    if parent_folder_id:
        parent_folder = Folder.objects.get(id=parent_folder_id)
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user  # Set the user for the folder
            folder.parent_folder = parent_folder 
            folder.save()
            if parent_folder:
                return redirect('subfolder',parent_folder_id=parent_folder_id)
            else:
                return redirect('all_files')

    else:
        form = FolderForm()
    return render(request, 'root/create_folder.html', {'folderform': form})


@login_required
def home(request):
    logged_user=request.user
    favorite_files = AllFiles.objects.filter(is_favorite=True,folder=None,owner=logged_user)
    favorite_folders = Folder.objects.filter(is_favorite=True, parent_folder=None,user=logged_user)
    context = {
        'files': favorite_files,
        'folders': favorite_folders,
    }
    return render(request, 'root/all_files.html',context )



def download_file(request, file_path):
    # Assuming file_path is the path to the file you want to download
    file_name=os.path.basename(file_path)
    file = open(file_path, 'rb')
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)  # Set the desired filename
    return response



def download_folder(request,pk):
    folder = get_object_or_404(Folder, pk=pk)
    folder_name = folder.name
    zip_subdir = folder_name
    zip_filename = zip_subdir + ".zip"
    byte_stream = io.BytesIO()
    zf = zipfile.ZipFile(byte_stream, "w")

    folder_list = Folder.objects.filter(parent_folder=folder)
    file_list = AllFiles.objects.filter(folder=folder)

    zf = zip_them_all(file_list,folder_list,zip_subdir,zf)

    zf.close()
    response = HttpResponse(byte_stream.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return response


def FolderUpload(request,pk):
    if request.method == 'POST':
        form = FolderUploadForm(request.POST, request.FILES)

        p = request.POST['path']

        print(p)
        print(p,1)
        file_path_list = []
        t = ""
        for i in range(len(p)):
            if p[i]!=",":
                t = t+p[i]
            else:
                file_path_list.append(t)
                t = ""

        pathlist_list = []

        for path in file_path_list:
            t = ""
            list = []
            for i in range(len(path)):
                if path[i]!='/':
                    t = t + path[i]
                else:
                    list.append(t)
                    t = ""
            pathlist_list.append(list)

        for path in pathlist_list:
            for i in range(len(path)):
                if i==0:
                    try:
                        link = Folder.objects.get(pk=pk)
                        fol = Folder.objects.get(parent_folder=link,name=path[i])
                    except Folder.DoesNotExist:
                        new_folder = Folder(name=path[i],parent_folder=link,user=request.user)
                        new_folder.save()
                        path[i] = new_folder
                    else:
                        path[i] = fol
                else:
                    try:
                        fol = Folder.objects.get(parent_folder=path[i-1],name=path[i])
                    except Folder.DoesNotExist:
                        new_folder = Folder(name=path[i],parent_folder=path[i-1],user=request.user)
                        new_folder.save()
                        path[i] = new_folder
                    else:
                        path[i] = fol


        if form.is_valid():
            index = 0
            for field in request.FILES.keys():
                for formfile in request.FILES.getlist(field):
                    pa = pathlist_list[index]


                    folder = pa[len(pa)-1]

                    f = AllFiles(file=formfile,owner=request.user,folder=folder )
                    f.name = f.filename()
                    f.save()
                    index = index+1

        return redirect('subfolder',pk)
    else:
        form = FolderUploadForm(None)
        return render(request,'root/folder_upload.html',{'form':form})


def zip_them_all(file_list,folder_list,zip_path,zf):
    for p in file_list:
        item = p
        file_name, file_extension = os.path.splitext(item.file.file.name)
        file_extension = file_extension[1:]
        x = -1*len(file_extension)
        response = HttpResponse(item.file.file,
            content_type = "file/%s" % file_extension)
        response["Content-Disposition"] = "attachment;"\
            "filename=%s.%s" %(slugify(item.title)[:x], file_extension)

        filename = slugify(item.title)[:x]
        filename = filename + "." + file_extension
        f1 = open(filename , 'wb')
        f1.write(response.content)
        f1.close()

        pa = os.path.join(zip_path,filename)
        zf.write(filename,pa, zipfile.ZIP_DEFLATED)


    for p in file_list:
        item = p
        file_name, file_extension = os.path.splitext(item.file.file.name)
        file_extension = file_extension[1:]
        x = -1*len(file_extension)
        filename = slugify(item.title)[:x]
        filename = filename + "." + file_extension

        location = os.path.abspath(filename)
        os.remove(location)


    for p in folder_list:
        dir = p.name
        z_path = os.path.join(zip_path, dir)
        fo_list = Folder.objects.filter(parent_folder=p)
        fi_list = AllFiles.objects.filter(folder=p)
        zf = zip_them_all(fi_list,fo_list,z_path,zf)


    return zf

def FolderUploadIndex(request):
    if request.method == 'POST':
        form = FolderUploadForm(request.POST, request.FILES)
        p = request.POST.get('path', '')
        file_path_list = []
        t = ""
        for i in range(len(p)):
            if p[i]!=",":
                t = t+p[i]
            else:
                file_path_list.append(t)
                t = ""

        pathlist_list = []

        for path in file_path_list:
            t = ""
            list = []
            for i in range(len(path)):
                if path[i]!='/':
                    t = t + path[i]
                else:
                    list.append(t)
                    t = ""
            pathlist_list.append(list)

        for path in pathlist_list:
            for i in range(len(path)):
                if i==0:
                    try:
                        fol = Folder.objects.get(parent_folder=None,name=path[i],user=request.user)
                    except Folder.DoesNotExist:
                        new_folder = Folder(name=path[i],user=request.user)
                        new_folder.save()
                        path[i] = new_folder
                    else:
                        path[i] = fol
                else:
                    try:
                        fol = Folder.objects.get(parent_folder=path[i-1],name=path[i])
                    except Folder.DoesNotExist:
                        new_folder = Folder(name=path[i],parent_folder=path[i-1],user=request.user)
                        new_folder.save()
                        path[i] = new_folder
                    else:
                        path[i] = fol


        if form.is_valid():
            index = 0
            for field in request.FILES.keys():
                for formfile in request.FILES.getlist(field):
                    pa = pathlist_list[index]
                    folder = pa[len(pa)-1]
                    f = AllFiles(file=formfile,owner=request.user,folder=folder )
                    f.name = f.filename()
                    f.save()
                    index = index+1

        return redirect('all_files')
    else:
        form = FolderUploadForm(None)
        return render(request,'root/folder_upload.html',{'form':form})



def toggle_favorite(request, model, pk):
        
        if model == 'File':
            item = get_object_or_404(AllFiles, pk=pk)
        elif model == 'Folder':
            item = get_object_or_404(Folder, pk=pk)
        else:
            return reverse('home')
        
        item.is_favorite = not item.is_favorite
        item.save()

        if item.is_favorite:
            messages.success(request, 'Added to favorites')
        else:
            messages.success(request, 'Removed from favorites')

        # Redirect back to the referring page
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # Redirect back to the referring page
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class MyFileFolderView(TemplateView):
    template_name = 'root/all_files.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id=None
        folder_id = self.kwargs.get('parent_folder_id')
        folderuser=None
        logged_user=None
        logged_user=self.kwargs.get('user_id')

        if logged_user:
            logged_user=self.kwargs.get('user_id')

        elif folder_id:
            folderuser=Folder.objects.get(id=folder_id)
            logged_user=folderuser.user

        else:
            logged_user=self.request.user    


        if folder_id:
            files = AllFiles.objects.filter(owner=logged_user,folder=folder_id)
        else:
            files = AllFiles.objects.filter(owner=logged_user, folder=None)

        if folder_id:
            folders = Folder.objects.filter(user=logged_user, parent_folder=folder_id)
        else:
            folders = Folder.objects.filter(user=logged_user, parent_folder=None)


        context['files'] = files
        context['folders'] = folders
        context['folderuser']=logged_user
        return context



class PostCreateView(LoginRequiredMixin, CreateView):
    model = AllFiles
    fields = ['title', 'file']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        file = self.request.FILES.get('file')
        if file:
            form.instance.file = file

        folder_id = self.kwargs.get('parent_folder_id')
        if folder_id:
            folder = Folder.objects.get(id=folder_id)
            form.instance.folder = folder

        response = super().form_valid(form)
        return response

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner
        
    def get_success_url(self):
        parent_folder_id = self.kwargs.get('parent_folder_id')
        if parent_folder_id:
            return reverse('subfolder', kwargs={'parent_folder_id': parent_folder_id})
        return reverse('all_files')
   


class FileDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AllFiles

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.owner
    
    def get_success_url(self):
      f = AllFiles.objects.get(pk=self.kwargs['pk'])
      folder = f.folder
      if not folder:
          return reverse('all_files')
      else:
          return reverse_lazy('subfolder',kwargs={'parent_folder_id': folder.pk})


class FolderDelete(DeleteView):
  model = Folder

  def get_success_url(self):
        f = Folder.objects.get(pk=self.kwargs['pk'])
        folder = f.parent_folder
        if not folder:
            return reverse('all_files')
        else:
            return reverse_lazy('subfolder',kwargs={'parent_folder_id': folder.pk})

  def get(self, *args, **kwargs):
            return self.post(*args, **kwargs)


