from nodeconductor.core import tasks as core_tasks

from backend import AzureBackendError


class StateException(Exception):
    pass


class PollCheckTask(core_tasks.Task):
    # TODO [TM:8/14/17] merge with OpenStack check task
    max_retries = 300
    default_retry_delay = 5

    @classmethod
    def get_description(cls, virtual_machine, backend_check_method, *args, **kwargs):
        return 'Check virtual machine "%s" with method "%s"' % (virtual_machine, backend_check_method)

    def get_backend(self, virtual_machine):
        return virtual_machine.get_backend()

    def execute(self, virtual_machine, backend_check_method):
        # backend_check_method should return True if object does not exist at backend
        backend = self.get_backend(virtual_machine)
        if not getattr(backend, backend_check_method)(virtual_machine):
            self.retry()
        return virtual_machine


class PollRuntimeStateTask(core_tasks.Task):
    max_retries = 300
    default_retry_delay = 5

    @classmethod
    def get_description(cls, virtual_machine, backend_pull_method, *args, **kwargs):
        return 'Poll virtual machine "%s" with method "%s"' % (virtual_machine, backend_pull_method)

    def get_backend(self, virtual_machine):
        return virtual_machine.get_backend()

    def execute(self, virtual_machine, backend_pull_method, success_state, erred_state):
        backend = self.get_backend(virtual_machine)
        try:
            getattr(backend, backend_pull_method)(virtual_machine)
        except AzureBackendError:
            self.retry()

        virtual_machine.refresh_from_db()
        if virtual_machine.runtime_state not in (backend.State.fromstring(success_state),
                                                 backend.State.fromstring(erred_state)):
            self.retry()
        elif virtual_machine.runtime_state == backend.State.fromstring(erred_state):
            raise StateException('%s %s (PK: %s) state become erred: %s' % (
                    virtual_machine.__class__.__name__, virtual_machine, virtual_machine.pk, erred_state))
        return virtual_machine
