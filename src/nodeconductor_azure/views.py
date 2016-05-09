from django.http import HttpResponse
from rest_framework import decorators, exceptions, viewsets

from nodeconductor.structure import ServiceBackendError, views as structure_views

from . import models, serializers
from .backend import SizeQueryset


class AzureServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AzureService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.VirtualMachineImportSerializer


class AzureServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AzureServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.Image.objects.order_by('name')


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SizeQueryset()
    serializer_class = serializers.SizeSerializer
    lookup_field = 'uuid'


class VirtualMachineViewSet(structure_views.BaseResourceViewSet):
    queryset = models.VirtualMachine.objects.all()
    serializer_class = serializers.VirtualMachineSerializer

    @decorators.detail_route()
    def rdp(self, request, uuid=None):
        vm = self.get_object()
        if vm.state != vm.States.ONLINE:
            raise exceptions.NotAcceptable("Can't launch remote desktop for offline virtual machine")

        try:
            backend = vm.get_backend()
            backend_vm = backend.get_vm(vm.backend_id)
            rdp_port = backend_vm.extra['remote_desktop_port']
        except ServiceBackendError as e:
            raise exceptions.APIException(e)

        if not rdp_port:
            raise exceptions.NotFound("This virtual machine doesn't run remote desktop")

        response = HttpResponse(content_type='application/x-rdp')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(backend_vm.name)
        response.write(
            "full address:s:%s.cloudapp.net:%s\n"
            "prompt for credentials:i:1\n\n" % (vm.service_project_link.cloud_service_name, rdp_port))

        return response

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'])
