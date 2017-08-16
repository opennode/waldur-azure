from __future__ import unicode_literals

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodeconductor.core.fields import JSONField
from nodeconductor.quotas.fields import CounterQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
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

    @classmethod
    def get_url_name(cls):
        return 'azure'

    class Quotas(QuotaModelMixin.Quotas):
        vm_count = CounterQuotaField(
            target_models=lambda: [VirtualMachine],
            path_to_scope='service_project_link.service'
        )


class AzureServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(AzureService)

    cloud_service_name = models.CharField(max_length=255, blank=True)

    def get_backend(self):
        return super(AzureServiceProjectLink, self).get_backend(
            cloud_service_name=self.cloud_service_name)

    @classmethod
    def get_url_name(cls):
        return 'azure-spl'


class Image(structure_models.GeneralServiceProperty):
    @classmethod
    def get_url_name(cls):
        return 'azure-image'


class Size(object):
    _meta = 'size'

    @classmethod
    def get_url_name(cls):
        return 'azure-size'


class VirtualMachine(structure_models.VirtualMachine):
    service_project_link = models.ForeignKey(
        AzureServiceProjectLink, related_name='virtualmachines', on_delete=models.PROTECT)
    public_ips = JSONField(default=[], help_text=_('List of public IP addresses'), blank=True)
    private_ips = JSONField(default=[], help_text=_('List of private IP addresses'), blank=True)
    remote_desktop_port = models.IntegerField(validators=[MaxValueValidator(65535)], null=True)

    @classmethod
    def get_url_name(cls):
        return 'azure-virtualmachine'

    def get_access_url_name(self):
        return 'azure-virtualmachine-rdp'

    @property
    def external_ips(self):
        return self.public_ips

    @property
    def internal_ips(self):
        return self.private_ips

    @classmethod
    def get_backend_fields(cls):
        return super(VirtualMachine, cls).get_backend_fields() + ('public_ips', 'private_ips')
