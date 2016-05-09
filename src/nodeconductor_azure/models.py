from __future__ import unicode_literals

from django.db import models

from nodeconductor.structure import models as structure_models


class AzureService(structure_models.Service):
    Locations = (('Central US', 'Central US'),
                 ('East US 2', 'East US 2'),
                 ('South Central US', 'South Central US'),
                 ('North Europe', 'North Europe'),
                 ('East Asia', 'East Asia'),
                 ('Southeast Asia', 'Southeast Asia'),
                 ('Japan West', 'Japan West'))

    projects = models.ManyToManyField(
        structure_models.Project, related_name='azure_services', through='AzureServiceProjectLink')


class AzureServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(AzureService)

    cloud_service_name = models.CharField(max_length=255, blank=True)

    def get_backend(self):
        return super(AzureServiceProjectLink, self).get_backend(
            cloud_service_name=self.cloud_service_name)


class Image(structure_models.GeneralServiceProperty):
    pass


class Size(object):
    _meta = 'size'

    @classmethod
    def get_url_name(cls):
        return 'azure-size'


class VirtualMachine(structure_models.VirtualMachineMixin, structure_models.Resource):
    service_project_link = models.ForeignKey(
        AzureServiceProjectLink, related_name='virtualmachines', on_delete=models.PROTECT)

    def get_access_url_name(self):
        return 'azure-virtualmachine-rdp'
