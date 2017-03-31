=====
Progs
=====

.. _common:

---------------
Adding Programs
---------------

Additional programs must be stored under the `Progs` directory. A basic
program is a subclass of `ProgDef` (defined under `template.py`) and
uses utilities from `common.py` for defining functionality.

For naming, the module name must be the binary name suffixed with '.py',
the subclass must be the same name as the binary.

Defining programs is explained in the next section


Example
=======

Let's explain using an example module, for the program `example`.

`example.py`::

    from .template import ProgDef # parent class
    from .common import RuleTree, Rule, RuleVLen, Section

    class example(ProgDef):
        
        def init(self):
            # implementation

        def get_default_path(self):
            # implementation

        def save(self):
            # implementation


------
Common
------
.. automodule:: Progs.common

.. autoclass:: ConfigElement
    :members:

.. autoclass:: RuleTree
    :members:

.. autoclass:: Rule
    :members:

.. autoclass:: RuleVLen
    :members:

.. autoclass:: Section
    :members:

.. _template:

--------
Template
--------
.. automodule:: Progs.template

.. autoclass:: ProgDef
    :members:
