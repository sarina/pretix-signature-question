Pretix Signature Capture
========================

|tests-badge| |style-badge|

.. |tests-badge| image:: https://github.com/sarina/pretix-signature-capture/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/sarina/pretix-signature-capture/actions/workflows/tests.yml
   :alt: Tests
.. |style-badge| image:: https://github.com/sarina/pretix-signature-capture/actions/workflows/style.yml/badge.svg
   :target: https://github.com/sarina/pretix-signature-capture/actions/workflows/style.yml
   :alt: Code Style

A `pretix`_ plugin that lets attendees draw a signature in response to a
question — useful for liability waivers, photo releases, code-of-conduct
acknowledgements, and other situations where a typed checkbox isn't enough.

The captured signature is stored as a PNG attached to the order's question
answer, and can be reviewed by event organizers from the control panel.

This plugin is a maintained continuation of the original (now unmaintained)
``pretix-signature-question`` and its later fork ``pretix-signature-question-2``.
The 2.0 release is rebranded as ``pretix-signature-capture`` to make the
break with those abandoned packages explicit; see the migration notes below
if you're upgrading from either of them.

Configuration / Usage
---------------------

Each event can enable this plugin in **Settings > Plugins > Customization**.

Once the plugin is enabled, you can add a question with type *file* to a
ticket. The name of the question must contain the word *signature*.
Instead of the upload dialog, the signature field is displayed.

(The identifier-based detection that replaces the label-text matching above
is being introduced as part of the 2.0 release work; this section will be
updated when that lands.)

Migrating from ``pretix-signature-question`` (1.x or ``-2``)
------------------------------------------------------------

The 2.0 release renames both the PyPI distribution
(``pretix-signature-capture``) and the Python module
(``pretix_signature_capture``). To migrate:

1. Uninstall the old package from your environment::

       pip uninstall pretix-signature-question
       # or, if you were using the unofficial fork:
       pip uninstall pretix-signature-question-2

2. Install this package::

       pip install pretix-signature-capture

3. Re-enable the plugin in **Settings > Plugins > Customization** for any
   events where you previously had it enabled.

Existing question answers (the captured signature PNGs already attached to
orders) are preserved — they live in Pretix's question-answer storage, not
in the plugin.

Accessibility note
------------------

Signature capture widgets based on canvas elements may not be fully accessible for blind or low-vision users. Event organizers are encouraged to provide an alternative verification method when possible, such as a confirmation checkbox or emailed waiver.


Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository.

3. Activate the virtual environment you use for pretix development.

4. Install all development dependencies (pretix, the plugin in editable
   mode, plus lint/test/build tooling)::

       make requirements

   If you only want to install the plugin itself,
   ``pip install -e .`` is sufficient.

5. Restart your local pretix server. You can now use the plugin from this
   repository for your events by enabling it in the 'plugins' tab in the
   settings.

To check your plugin for code-style violations (matches what CI runs)::

    make lint

To auto-fix the issues those checks flag::

    docformatter -r .
    isort .
    black .

To automatically check for these issues before you commit, you can run
``.install-hooks``.

i18n
----

Translation support is intentionally not wired into the build for the
2.0 release. The ``locale/`` directory and ``Makefile`` are kept in
place because they hold existing translation work, but compiled ``.mo``
files are not produced or shipped. Restoring a working translations
build is planned for a follow-up release.

Acknowledgements
----------------

This plugin descends from the original ``pretix-signature-question`` by the
pretix team and the subsequent unofficial fork
(``pretix-unofficial/pretix-signature-question`` on GitHub, published as
``pretix-signature-question-2`` on PyPI). The 2.0 release rebrands and
modernizes that lineage.

License
-------

Copyright 2021 pretix

Copyright 2026 Sarina Canelake

Released under the terms of the Apache License 2.0.

.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
