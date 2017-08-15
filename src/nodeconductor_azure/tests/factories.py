from django.urls import reverse
from libcloud.compute.types import NodeState

import factory
from factory import fuzzy

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor.structure import models as structure_models

from .. import models


class AzureServiceSettingsFactory(structure_factories.ServiceSettingsFactory):
    class Meta(object):
        model = structure_models.ServiceSettings

    type = 'Azure'


class AzureServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.AzureService

    settings = factory.SubFactory(AzureServiceSettingsFactory)
    customer = factory.SelfAttribute('settings.customer')

    @classmethod
    def get_url(cls, service=None, action=None):
        if service is None:
            service = AzureServiceFactory()
        url = 'http://testserver' + reverse('azure-detail', kwargs={'uuid': service.uuid})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('azure-list')


class AzureServiceProjectLinkFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.AzureServiceProjectLink

    service = factory.SubFactory(AzureServiceFactory)
    project = factory.SubFactory(structure_factories.ProjectFactory)

    @classmethod
    def get_url(cls, spl=None, action=None):
        if spl is None:
            spl = AzureServiceProjectLinkFactory()
        url = 'http://testserver' + reverse('azure-spl-detail', kwargs={'pk': spl.pk})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('azure-spl-list')


class VirtualMachineFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.VirtualMachine

    name = factory.Sequence(lambda n: 'virtual-machine%s' % n)
    backend_id = factory.Sequence(lambda n: 'virtual-machine-id%s' % n)
    service_project_link = factory.SubFactory(AzureServiceProjectLinkFactory)

    state = models.VirtualMachine.States.OK
    runtime_state = NodeState.RUNNING
    cores = fuzzy.FuzzyInteger(1, 8, step=2)
    ram = fuzzy.FuzzyInteger(1024, 10240, step=1024)
    disk = fuzzy.FuzzyInteger(1024, 102400, step=1024)

    @classmethod
    def get_url(cls, instance=None, action=None):
        if instance is None:
            instance = VirtualMachineFactory()
        url = 'http://testserver' + reverse('azure-virtualmachine-detail', kwargs={'uuid': instance.uuid})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('aws-virtualmachine-list')
