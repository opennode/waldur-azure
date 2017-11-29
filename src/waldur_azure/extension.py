from nodeconductor.core import NodeConductorExtension


class AzureExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'waldur_azure'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def get_cleanup_executor():
        from .executors import AzureCleanupExecutor
        return AzureCleanupExecutor
