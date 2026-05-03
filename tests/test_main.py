"""Smoke tests for the plugin scaffolding.

The goal of this module is to prove that the test environment (pretix
test settings, DB, plugin loader, template/static finders) is wired up
correctly. Per-feature tests live in their own modules.
"""

import pytest
from django_scopes import scopes_disabled

from pretix_signature_capture.signals import html_head_presale


@pytest.mark.django_db
def test_html_head_presale_renders_plugin_script_tags(event):
    """The html_head receiver should return rendered HTML referencing
    the plugin's bundled JS via ``{% static %}``."""
    rendered = html_head_presale(sender=event, request=None)

    assert isinstance(rendered, str)
    assert "<script" in rendered
    # Templates use {% static "pretix_signature_capture/<file>" %} so the
    # rendered URL contains this path segment regardless of STATIC_URL.
    assert "pretix_signature_capture/jSignature.min.js" in rendered
    assert "pretix_signature_capture/main.js" in rendered


@pytest.mark.django_db
@scopes_disabled()
def test_cart_position_fixture_is_wired_up(cart_position, file_question):
    """Sanity check that the conftest fixtures compose correctly:
    a cart position whose item has a file-type question attached.

    The conftest ``pytest_fixture_setup`` hook disables django-scopes for
    fixture *creation* but not for the test body, so any in-body queries
    on scoped models (Item, Question, ...) need an explicit
    ``@scopes_disabled()`` decorator. Mirrors how pretix's own tests
    handle this — e.g. ``tests/plugins/sendmail/test_rules.py``.
    """
    assert cart_position.pk is not None
    assert cart_position.item.questions.filter(pk=file_question.pk).exists()
    assert file_question.type == "F"
