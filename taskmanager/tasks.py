from celery import Celery
from taskmanager.models import Feed

app = Celery('tasks', broker='amqp://guest@localhost//')

@app.task
def add_feed(user, task):
	feed = Feed(user=user, activity='You added task: '+ str(task))
	feed.save()
	return 'You added task: ' + str(task)

@app.task
def delete_feed(user, task):
	feed = Feed(user=user, activity='You deleted task: '+ str(task))
	feed.save()
	return 'You deleted task: ' + str(task)

@app.task
def complete_feed(user, task):
	feed = Feed(user=user, activity='You completed task: '+ str(task))
	feed.save()
	return 'You completed task: ' + str(task)	

@app.task
def user_login(id):
	f = open("login.txt", "a")
	f.write(str(id) + ' logged in.\n')
	f.close()
	print f
	return str(id) + ' logged in.'
