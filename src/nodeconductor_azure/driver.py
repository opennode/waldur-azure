from libcloud.utils.py3 import httplib

try:
    from lxml import etree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from libcloud.common.azure import AzureServiceManagementConnection as _AzureServiceManagementConnection
from libcloud.common.azure import AzureResponse as _AzureResponse
from libcloud.compute.drivers.azure import AzureNodeDriver as _AzureNodeDriver
from libcloud.common.types import InvalidCredsError
from libcloud.common.types import LibcloudError, MalformedResponseError


def fixxpath(root, xpath):
    """ElementTree wants namespaces in its xpaths, so here we add them."""
    namespace, root_tag = root.tag[1:].split("}", 1)
    fixed_xpath = "/".join(["{%s}%s" % (namespace, e)
                            for e in xpath.split("/")])
    return fixed_xpath


def parse_error(body):
    code = body.findtext(fixxpath(body, 'Code'))
    message = body.findtext(fixxpath(body, 'Message'))
    message = message.split('\n')[0]
    error_msg = '%s: %s' % (code, message)
    return error_msg


class AzureResponse(_AzureResponse):
    """
    Fix error parsing for Azure
    """
    def parse_error(self, msg=None):
        error_msg = 'Unknown error'

        try:
            # Azure does give some meaningful errors, but is inconsistent
            # Some APIs respond with an XML error. Others just dump HTML
            body = self.parse_body()

            if ET.iselement(body):
                error_msg = parse_error(body)

        except MalformedResponseError:
            pass

        if msg:
            error_msg = '%s - %s' % (msg, error_msg)

        if self.status in [httplib.UNAUTHORIZED, httplib.FORBIDDEN]:
            raise InvalidCredsError(error_msg)

        raise LibcloudError(
            '%s Status code: %d.' % (error_msg, self.status),
            driver=self
        )


class AzureServiceManagementConnection(_AzureServiceManagementConnection):
    responseCls = AzureResponse


class AzureNodeDriver(_AzureNodeDriver):
    connectionCls = AzureServiceManagementConnection

    def raise_for_response(self, response, valid_response):
        if response.status != valid_response:
            error_msg = response.body
            try:
                body = ET.XML(error_msg)
                if ET.iselement(body):
                    error_msg = parse_error(body)
            except:
                pass

            values = (response.error, error_msg, response.status)
            message = 'Message: %s, Body: %s, Status code: %s' % (values)
            raise LibcloudError(message, driver=self)
