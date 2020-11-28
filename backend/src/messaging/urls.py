from django.urls import path

from messaging.api.views import ChannelCreateView, ChannelListView

app_name = "messaging"

urlpatterns = [
    path("createChannel/", ChannelCreateView.as_view(), name="create-channel"),
    path("getChannels/", ChannelListView.as_view(), name="get-channel-list"),
    # path("<uuid:channel_id>/get/", ChannelListView.as_view(), name="get-channel-list"),
    # path('getbyempid/<int:emp_id>/<uuid:factory_id>', views.empdetails)
]