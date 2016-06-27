import re

from django.utils import six, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.core import serializers as core_serializers
from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AzureBackendError, SizeQueryset


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'username': 'In the format of GUID',
        'certificate': 'X509 certificate in .PEM format',
    }
    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'location': '',
        'cloud_service_name': '',
        'images_regex': ''
    }

    location = serializers.ChoiceField(
        choices=models.AzureService.Locations,
        write_only=True,
        required=False,
        allow_blank=True)

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AzureService
        view_name = 'azure-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['username'].label = 'Subscription ID'
        fields['username'].required = True

        fields['certificate'].label = 'Private certificate file'
        fields['certificate'].required = True
        fields['certificate'].write_only = True

        fields['location'].help_text = 'Azure region where to provision resources (default: "Central US")'
        fields['cloud_service_name'].help_text = 'If defined all connected SPLs will operate in the defined cloud service group'
        fields['images_regex'].help_text = 'Regular expression to limit images list'
        return fields

    def validate_certificate(self, value):
        if value:
            try:
                x509.load_pem_x509_certificate(value.read(), default_backend())
            except ValueError:
                raise serializers.ValidationError("Valid X509 certificate in .PEM format is expected")

        return value


class ImageSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Image
        view_name = 'azure-image-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class SizeSerializer(six.with_metaclass(structure_serializers.PropertySerializerMetaclass,
                                        serializers.Serializer)):

    uuid = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    cores = serializers.ReadOnlyField()
    ram = serializers.ReadOnlyField()
    disk = serializers.ReadOnlyField()

    class Meta(object):
        model = models.Size

    def get_url(self, size):
        return reverse('azure-size-detail', kwargs={'uuid': size.uuid}, request=self.context.get('request'))


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.AzureServiceProjectLink
        view_name = 'azure-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'azure-detail'},
        }


class VirtualMachineSerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='azure-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='azure-spl-detail',
        queryset=models.AzureServiceProjectLink.objects.all())

    image = serializers.HyperlinkedRelatedField(
        view_name='azure-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='azure-size-detail',
        lookup_field='uuid',
        queryset=SizeQueryset(),
        write_only=True)

    external_ips = serializers.ListField(
        child=core_serializers.IPAddressField(),
        read_only=True,
    )

    username = serializers.CharField(write_only=True, required=True)
    # XXX: it's rather insecure
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    rdp = serializers.HyperlinkedIdentityField(view_name='azure-virtualmachine-rdp', lookup_field='uuid')

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'image', 'size', 'username', 'password', 'user_data', 'rdp', 'external_ips'
        )
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'image', 'size', 'username', 'password', 'user_data'
        )

    def validate(self, attrs):
        if not re.match(r'[a-zA-Z][a-zA-Z0-9-]{0,13}[a-zA-Z0-9]$', attrs['name']):
            raise serializers.ValidationError(
                {'name': "The name can contain only letters, numbers, and hyphens. "
                         "The name must be shorter than 15 characters and start with "
                         "a letter and must end with a letter or a number."})

        # passwords must contain characters from at least three of the following four categories:
        groups = (r'[a-z]', r'[A-Z]', r'[0-9]', r'[^a-zA-Z\d\s:]')
        if not 6 <= len(attrs['password']) <= 72 or sum(bool(re.search(g, attrs['password'])) for g in groups) < 3:
            raise serializers.ValidationError({
                'password': "The supplied password must be 6-72 characters long "
                "and contain 3 of the following: a lowercase character, "
                "an uppercase character, a number, a special character."})

        if re.match(r'Administrator|Admin', attrs['username'], re.I):
            raise serializers.ValidationError({
                'username': "Invalid Windows administrator username."})

        return attrs


class VirtualMachineImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'
        fields = structure_serializers.BaseResourceImportSerializer.Meta.fields + (
            'cores', 'ram', 'disk',
            'external_ips', 'internal_ips',
        )

    def create(self, validated_data):
        spl = validated_data['service_project_link']
        backend = spl.get_backend()

        try:
            vm = backend.get_vm(validated_data['backend_id'])
        except AzureBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find Virtual Machine with ID %s" % validated_data['backend_id']})

        validated_data['name'] = vm.name
        validated_data['created'] = timezone.now()
        validated_data['ram'] = vm.size.ram
        validated_data['disk'] = vm.size.disk
        validated_data['cores'] = 'Shared' and 1 or vm.size.extra['cores']
        validated_data['external_ips'] = vm.public_ips[0]
        validated_data['internal_ips'] = vm.private_ips[0]
        validated_data['state'] = models.VirtualMachine.States.ONLINE \
            if vm.state == backend.State.RUNNING else models.VirtualMachine.States.OFFLINE

        return super(VirtualMachineImportSerializer, self).create(validated_data)
