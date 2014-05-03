from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django import forms
from .forms import UserCreationForm
from taskmanager.models import MyUserManager, MyUser, Task, Feed
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import datetime
from tasks import add_feed, delete_feed, complete_feed, user_login


# Create your views here.
def landing(request):
	return render(request, 'taskmanager/landing.html')

def auth_login(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(email=email, password=password)
		if user is not None:
			login(request, user)
			user_login.delay(email)
			return HttpResponseRedirect("/tasks/")
		else:			
			return HttpResponse('Invalid login.')
	else:
		form = UserCreationForm()
	return render(request, "registration/login.html", {
		'form': form,
	})
    
def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
			new_user = authenticate(email=request.POST['email'], password=request.POST['password1'])
			login(request, new_user)
			user_login.delay(str(request.POST['email']))
			return HttpResponseRedirect("/tasks/")
	else:
		form = UserCreationForm()
	return render(request, "registration/register.html", {
		'form': form,
	})

def auth_logout(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def tasks(request):
	tasks_remaining = Task.objects.filter(user=request.user, completed=False)
	tasks_completed = Task.objects.filter(user=request.user, completed=True)
	feed_list = Feed.objects.filter(user=request.user).order_by('-timestamp')[:10]
	
	if request.method == 'POST':
		if 'name' in request.POST:
			tasks_remaining = Task.objects.filter(user=request.user, completed=False).extra(select={'lower_name':'lower(name)'}).order_by('lower_name')
			tasks_completed = Task.objects.filter(user=request.user, completed=True).extra(select={'lower_name':'lower(name)'}).order_by('lower_name')
			#return HttpResponseRedirect(reverse('tasks'))
			return render(request, 'taskmanager/tasks.html', {'tasks_remaining': tasks_remaining, 'tasks_completed': tasks_completed, 'feed_list': feed_list })
		elif 'date_added' in request.POST:
			tasks_remaining = Task.objects.filter(user=request.user, completed=False).order_by('date_added')
			tasks_completed = Task.objects.filter(user=request.user, completed=True).order_by('date_added')
			return render(request, 'taskmanager/tasks.html', {'tasks_remaining': tasks_remaining, 'tasks_completed': tasks_completed, 'feed_list': feed_list })
		elif 'date_completed' in request.POST:
			tasks_remaining = Task.objects.filter(user=request.user, completed=False).order_by('date_completed')
			tasks_completed = Task.objects.filter(user=request.user, completed=True).order_by('date_completed')
			return render(request, 'taskmanager/tasks.html', {'tasks_remaining': tasks_remaining, 'tasks_completed': tasks_completed, 'feed_list': feed_list })
		elif 'deadline' in request.POST:
			tasks_remaining = Task.objects.filter(user=request.user, completed=False).order_by('deadline')
			tasks_completed = Task.objects.filter(user=request.user, completed=True).order_by('deadline')
			return render(request, 'taskmanager/tasks.html', {'tasks_remaining': tasks_remaining, 'tasks_completed': tasks_completed, 'feed_list': feed_list })

	return render(request, 'taskmanager/tasks.html', {'tasks_remaining': tasks_remaining, 'tasks_completed': tasks_completed, 'feed_list': feed_list })
	
@login_required
def add_task(request):
	if request.method == 'POST':
		name = request.POST.get('name', '')
		deadline = request.POST.get('deadline', '')
		deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d").date()
		today = datetime.date.today()
		if deadline >= today:
			task = Task(user=request.user, name=name, deadline=deadline)
			task.save()
			add_feed.delay(request.user, task.name)
			#feed = Feed(user=request.user, activity='You added task: '+ task.name)
			#feed.save()
			return HttpResponseRedirect(reverse('tasks'))
		else:
			return HttpResponse('Deadline cannot be before current date.')
	return render(request, 'taskmanager/add_task.html')

@login_required
def task_details(request, task_id):
	task = get_object_or_404(Task, id=task_id)
	if request.user != task.user:
		return HttpResponse("You don't have permission to view this task.")
	if request.method == 'POST':
		if 'complete' in request.POST:
			task.completed = True
			task.date_completed = datetime.date.today()
			task.save()
			complete_feed.delay(request.user, task.name)
			#feed = Feed(user=request.user, activity='You completed task: '+ task.name)
			#feed.save()
		elif 'incomplete' in request.POST:
			task.completed = False
			task.date_completed = None
			task.save()
			add_feed.delay(request.user, task.name)
			#feed = Feed(user=request.user, activity='You added task: '+ task.name)
			#feed.save()
		elif 'delete' in request.POST:
			task.delete()
			delete_feed.delay(request.user, task.name)
			#feed = Feed(user=request.user, activity='You deleted task: '+ task.name)
			#feed.save()
			return HttpResponseRedirect(reverse('tasks'))
	return render(request, 'taskmanager/task_details.html', {'task': task})
