from django.http import HttpResponse

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader
from forms import UserForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
import models


#This is a test view
def index(request):
    return HttpResponse("OneDir says hello world!")

#This view is the login page
def login(request):
	return render(request, 'onedir/login.html')

#This view is the user registration page
def register(request):
	return render(request, 'onedir/register.html')

#This view is the user's homepage after logging in.
#Should contain list of files in the OneDir server
def homepage(request, username):
	context = {'username': username}
	return render(request, 'onedir/userhome.html', context)

#This view is when the user wishes to change his password
def changepw(request, username):
	html = \
		"<html>" \
		"<body>The user %s would like to change his password " \
		"</body>" \
		"<button type=""button"">Click Me!</button>" \
		"</html>" %username
	return HttpResponse(html)

#This is the UserForm view used for registration
def register_user(request):
	context = RequestContext(request)

	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)

		if user_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()

			registered = True
		else:
			print user_form.errors

	return render_to_response(
		'OneDir/register.html',
		{'user_form':user_form, 'registered':registered},
		context
	)

def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']


        user = authenticate(username=username, password=password)


        if user is not None:
            # Is the account active
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # Send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/onedir/')
            else:
                return HttpResponse("Your OneDir account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('onedir/login.html', {}, context)