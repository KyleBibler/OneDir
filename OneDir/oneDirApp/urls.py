__author__ = 'Owner'

from django.conf.urls import patterns, url
from oneDirApp import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')),
    #url(r'^register/$', views.register, name='register'),