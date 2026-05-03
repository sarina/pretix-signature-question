"""Pytest fixtures for pretix-signature-capture tests.

Pretix's own test conftest (under ``pretix/src/tests/``) provides a
``pytest_fixture_setup`` hook that auto-disables django-scopes for any
non-generator fixture. Out-of-tree plugin tests don't run under that
parent conftest, so we replicate the hook here. Without it, every fixture
that touches a scoped model (Event, Item, Question, CartPosition, ...)
would need its own ``with scopes_disabled():`` block.

Reference: ``pretix/src/tests/conftest.py``.
"""

import datetime
import inspect

import pytest
from django.utils.timezone import now
from django_scopes import scope, scopes_disabled

from pretix.base.models import (
    CartPosition,
    Event,
    Item,
    Organizer,
    Question,
)


@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef, request):
    """Disable django-scopes for non-generator fixtures (mirrors pretix)."""
    if inspect.isgeneratorfunction(fixturedef.func):
        yield
    else:
        with scopes_disabled():
            yield


@pytest.fixture
def organizer():
    """A bare Organizer with slug ``dummy``."""
    org = Organizer.objects.create(name="Dummy", slug="dummy")
    with scope(organizer=org):
        yield org


@pytest.fixture
def event(organizer):
    """An Event under ``organizer`` with this plugin enabled."""
    return Event.objects.create(
        organizer=organizer,
        name="Dummy Event",
        slug="dummy",
        date_from=now(),
        live=True,
        plugins="pretix_signature_capture",
    )


@pytest.fixture
def item(event):
    """A simple paid Item attached to ``event``."""
    return Item.objects.create(event=event, name="Ticket", default_price=23)


@pytest.fixture
def file_question(event, item):
    """A file-upload Question attached to ``item``.

    This is the question type the plugin extends — see issue #5+ for the
    label-text-marker -> proper-API migration.
    """
    q = Question.objects.create(
        event=event,
        question="Signature",
        type=Question.TYPE_FILE,
        required=False,
    )
    item.questions.add(q)
    return q


@pytest.fixture
def cart_position(event, item, file_question):
    """A CartPosition for ``item`` in a fresh cart, with ``file_question`` attached.

    Returns the CartPosition; the related question is reachable via
    ``cart_position.item.questions.first()``.
    """
    return CartPosition.objects.create(
        event=event,
        cart_id="dummy_cart",
        item=item,
        price=23,
        expires=now() + datetime.timedelta(minutes=10),
    )
