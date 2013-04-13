from django.conf.urls import patterns, url
from meetings import views


urlpatterns = patterns('',

    url(r'^meeting/$', views.MeetingList.as_view(), name="meetings" ),

    url(r'^meeting/create/$', views.MeetingCreateView.as_view(),
        name="meeting_create" ),

    url(r'^meeting/(?P<pk>\d+)/$', views.MeetingDetailView.as_view(), 
        name="meeting" ),

    url(r'^meeting/(?P<pk>\d+)/close/$', views.CloseMeetingView.as_view(),
        name="meeting_close" ),

#    url(r'^issues/(?P<pk>\d+)/create-proposal/$', views.ProposalCreateView.as_view(), name="proposal_create" ),

)