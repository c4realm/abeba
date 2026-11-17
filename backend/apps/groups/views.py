from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from services import groups as group_service

from .models import Group, Membership
from .serializers import GroupCreateSerializer, GroupSerializer

ACTIVE_MEMBERSHIP = [Membership.Status.PENDING, Membership.Status.APPROVED, Membership.Status.ACTIVE]


def groups_visible_to(user):
    """The ONLY groups this user may see. Filtering here means other people's groups simply do not exist
    for them (a 404), which blocks 'insecure direct object reference' attacks."""
    return Group.objects.filter(memberships__user=user, memberships__status__in=ACTIVE_MEMBERSHIP).distinct()


class GroupListCreate(generics.ListCreateAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return groups_visible_to(self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        incoming = GroupCreateSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        try:
            group = group_service.create_group(request.user, **incoming.validated_data)
        except group_service.RuleViolation as err:
            if err.code == "restricted":
                raise PermissionDenied(err.message) from err
            raise ValidationError({"detail": err.message}) from err
        return Response(GroupSerializer(group, context={"request": request}).data, status=201)


class GroupDetail(generics.RetrieveAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return groups_visible_to(self.request.user)
