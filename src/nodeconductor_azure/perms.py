from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('nodeconductor_azure.AzureService', structure_perms.service_permission_logic),
    ('nodeconductor_azure.AzureServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('nodeconductor_azure.VirtualMachine', structure_perms.resource_permission_logic),
    ('nodeconductor_azure.Image', StaffPermissionLogic(any_permission=True)),
)
