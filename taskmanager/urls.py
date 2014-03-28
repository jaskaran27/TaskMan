from django.conf.urls import patterns, url

from taskmanager import views

urlpatterns = patterns('',
    url(r'^$', views.landing, name='landing'),
    url(r'^login/$', 'taskmanager.views.auth_login', name='auth_login'),
    url(r'^logout/$', 'taskmanager.views.auth_logout', name='auth_logout'),
    url(r'^register/$', 'taskmanager.views.register', name='register'),
    url(r'^tasks/$', 'taskmanager.views.tasks', name='tasks'),
    url(r'^tasks/add/$', 'taskmanager.views.add_task', name='add_task'),
    url(r'^tasks/(?P<task_id>.+)/$', 'taskmanager.views.task_details', name='task_details'),
)
