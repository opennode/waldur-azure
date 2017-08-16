from nodeconductor.structure import filters as structure_filters

from . import models


class ImageFilter(structure_filters.ServicePropertySettingsFilter):
    class Meta(structure_filters.ServicePropertySettingsFilter.Meta):
        model = models.Image
