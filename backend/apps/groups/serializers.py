from decimal import Decimal

from rest_framework import serializers

from .models import Group


class GroupCreateSerializer(serializers.Serializer):
    """Whitelist of what a client may send. Anything else (organizer, status, invite_code...) is ignored."""
    name = serializers.CharField(min_length=3, max_length=80, trim_whitespace=True)
    member_count = serializers.IntegerField(min_value=3, max_value=50)
    contribution = serializers.DecimalField(max_digits=12, decimal_places=2,
                                            min_value=Decimal("50"), max_value=Decimal("100000"))
    frequency = serializers.ChoiceField(choices=["weekly", "biweekly", "monthly"])


class GroupSerializer(serializers.ModelSerializer):
    """What we send back. The invite code is only shown to the organizer."""
    organizer = serializers.CharField(source="organizer.full_name", read_only=True)
    is_organizer = serializers.SerializerMethodField()
    invite_code = serializers.SerializerMethodField()
    terms_hash = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "member_count", "contribution", "frequency", "payout_model", "status",
                  "organizer", "is_organizer", "invite_code", "terms_hash", "created_at"]
        read_only_fields = fields

    def get_is_organizer(self, group) -> bool:
        return group.organizer_id == self.context["request"].user.id

    def get_invite_code(self, group):
        return group.invite_code if self.get_is_organizer(group) else None

    def get_terms_hash(self, group):
        terms = group.terms.order_by("-version").first()
        return terms.terms_hash if terms else None
