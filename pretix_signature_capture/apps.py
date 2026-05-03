from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2026.0.0 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_signature_capture"
    verbose_name = "Signature Capture"

    class PretixPluginMeta:
        name = gettext_lazy("Signature Capture")
        author = "Sarina Canelake"
        description = gettext_lazy(
            "Allows attendees to draw a signature in response to a question."
        )
        visible = True
        version = __version__
        category = "CUSTOMIZATION"
        compatibility = "pretix>=2026.0.0"

    def ready(self):
        from . import signals  # NOQA
