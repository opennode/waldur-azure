from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, throttle, transition, retry_if_false

from .models import VirtualMachine
from .backend import AzureBackendError


@shared_task(name='nodeconductor.azure.provision')
def provision(vm_uuid, **kwargs):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    with throttle(key=vm.service_project_link.to_string()):
        chain(
            provision_vm.si(vm_uuid, **kwargs),
            wait_for_vm_state.si(vm_uuid, 'RUNNING'),
        ).apply_async(
            link=set_online.si(vm_uuid),
            link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.azure.destroy')
@transition(VirtualMachine, 'begin_deleting')
@save_error_message
def destroy(vm_uuid, transition_entity=None):
    vm = transition_entity
    with throttle(key=vm.service_project_link.to_string()):
        try:
            backend = vm.get_backend()
            backend.destroy_vm(vm)
        except:
            set_erred(vm_uuid)
            raise
        else:
            vm.delete()


@shared_task(name='nodeconductor.azure.start')
def start(vm_uuid):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    with throttle(key=vm.service_project_link.to_string()):
        chain(
            begin_starting.s(vm_uuid),
            wait_for_vm_state.si(vm_uuid, 'RUNNING'),
        ).apply_async(
            link=set_online.si(vm_uuid),
            link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.azure.stop')
def stop(vm_uuid):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    with throttle(key=vm.service_project_link.to_string()):
        chain(
            begin_stopping.s(vm_uuid),
            wait_for_vm_state.si(vm_uuid, 'STOPPED'),
        ).apply_async(
            link=set_offline.si(vm_uuid),
            link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.azure.restart')
def restart(vm_uuid):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    with throttle(key=vm.service_project_link.to_string()):
        chain(
            begin_restarting.s(vm_uuid),
            wait_for_vm_state.si(vm_uuid, 'RUNNING'),
        ).apply_async(
            link=set_online.si(vm_uuid),
            link_error=set_erred.si(vm_uuid))


@shared_task(max_retries=300, default_retry_delay=3)
@retry_if_false
def wait_for_vm_state(vm_uuid, state=''):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    try:
        backend = vm.get_backend()
        backend_vm = backend.get_vm(vm.backend_id)
    except AzureBackendError:
        return False
    return backend_vm.state == backend.State.fromstring(state)


@shared_task(is_heavy_task=True)
@transition(VirtualMachine, 'begin_provisioning')
@save_error_message
def provision_vm(vm_uuid, transition_entity=None, **kwargs):
    vm = transition_entity
    backend = vm.get_backend()
    backend.provision_vm(vm, **kwargs)


@shared_task
@transition(VirtualMachine, 'begin_starting')
@save_error_message
def begin_starting(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.start_vm(vm)


@shared_task
@transition(VirtualMachine, 'begin_stopping')
@save_error_message
def begin_stopping(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.stop_vm(vm)


@shared_task
@transition(VirtualMachine, 'begin_restarting')
@save_error_message
def begin_restarting(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.reboot_vm(vm)


@shared_task
@transition(VirtualMachine, 'set_online')
def set_online(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = timezone.now()
    vm.save(update_fields=['start_time'])


@shared_task
@transition(VirtualMachine, 'set_offline')
def set_offline(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = None
    vm.save(update_fields=['start_time'])


@shared_task
@transition(VirtualMachine, 'set_erred')
def set_erred(vm_uuid, transition_entity=None):
    pass
