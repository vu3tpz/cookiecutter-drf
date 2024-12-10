from rest_framework import serializers

from apps.access.models import User
from apps.common.serializers import AppReadOnlyModelSerializer


class SimpleUserSerializer(AppReadOnlyModelSerializer):
    """
    Serializer to display simple user details.
    """

    full_name = serializers.CharField(source="get_full_name")

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = ["id", "uuid", "full_name"]
