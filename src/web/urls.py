from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.web_index, name='index'),
    url(r'^main$', views.web_main, name='main'),
    url(r'^upload$', views.web_upload_file, name='upload'),
    url(r'^type_in$', views.web_type_in, name='type_in'),
    url(r'^status$', views.web_status, name='status'),
    url(r'^about$', views.web_about, name='about'),
    url(r'^documentation$', views.web_documentation, name='documentation'),
    url(r'^contact$', views.web_contact, name='contact') 
]
