from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from messaging.api.serializers import ChannelSerializer
from messaging.models import Channel, Participant


class ChannelCreateView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # TODO(jonas): handle icon fetching
        channel = Channel.objects.create(icon="")
        Participant.objects.create(user=request.user, channel=channel, is_active=True)
        data = {"success": True, "channel": {"id": channel.id, "icon": channel.icon}}
        return Response(data=data, status=status.HTTP_200_OK)


class ChannelListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChannelSerializer

    def get_queryset(self):
        return Channel.objects.filter(users=self.request.user)
