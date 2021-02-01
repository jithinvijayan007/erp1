from enquiry.models import AddAttachments
from rest_framework.serializers import (
ModelSerializer
)

class AttachmentSerilaizer(ModelSerializer):
    class Meta:
        model = AddAttachments
        fields = '__all__'
