from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
import oneDirApp.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'OneDir.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/', include('oneDirApp.urls')),
    #rl(r'^login/$', oneDirApp.views.login),
	#url(r'^register/$', oneDirApp.views.register_user()),
	url(r'^user/(\w+)/$', oneDirApp.views.homepage),
	url(r'^user/(\w+)/changepw/$', oneDirApp.views.changepw),
    url(r'^register/$', oneDirApp.views.register_user, name='register'),
    url(r'^login/$', oneDirApp.views.user_login, name='login'),
)
