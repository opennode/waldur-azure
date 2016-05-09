from django.apps import AppConfig


class AzureConfig(AppConfig):
    name = 'nodeconductor_azure'
    verbose_name = "NodeConductor Azure"
    service_name = 'Azure'
    is_public_service = True

    def ready(self):
        from nodeconductor.cost_tracking import CostTrackingRegister
        from nodeconductor.structure import SupportedServices

        from .backend import AzureBackend
        from .cost_tracking import AzureCostTrackingBackend

        SupportedServices.register_backend(AzureBackend)
        CostTrackingRegister.register(self.label, AzureCostTrackingBackend)
