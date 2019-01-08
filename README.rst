=============================
zerial
=============================

.. image:: https://badge.fury.io/py/zerial.png
    :target: http://badge.fury.io/py/zerial

.. image:: https://travis-ci.org/jriddy/zerial.png?branch=master
    :target: https://travis-ci.org/jriddy/zerial

.. _attrs: http://www.attrs.org/en/stable/

Zerial is the serialization tool that allows your model classes to be the Zingle
Zource of Truth™ for your project.  Let your model classes take whatever form
or use whatever collection types they need, and just use metadata to define
how that text gets serialized.  With support for variant record types, you can
even evolve your data models over time, and even create versioned models if
need be.

Zerial is built on top of the excellent attrs_ library, which makes class
creation and definition in Python very easy and very obvious.  This library
adds abritrarily recursive serialization and de-serialization of complex
data classes.

Zerial was inspired because complex applications in spaces where requirements
are hard to define up front call for a unique approach to modeling data.  A
solution has to be flexible enough to accomodate a growing and changing
understanding of the underlying problem domain, while being rigorous enough
to encapsulate these changes to data modules.  External schemas like ORM or
JSON Schema are both inflexible and instrinsically bound to specific data
exchange formats (SQL and JSON) that you may or may not want to actually use.
Implicit schemas, although sufficienty flexible, ultimately fail because they
break separation of concerns, requiring every bit of code that touches data
to understand how to create a validate an entire history of model versions
for that data type.

This project aims to allow components to structure their data in a way that is
convenient for people interacting with the code, provided that it can be
destructured into simple types.  The combination of attrs_' rich support for
defaults and value factories and zerial's support of variant records,  you can
evolve your data models over time, without breaking your client code or stored
serialized data.


Features
--------

* Stucturing and destructuring of model classes
* Supports rich typing without any runtime dependency on stuff from the
  ``typing`` module, which has deeply inconsistent runtime behavior
* Model fields can be simple types or other model classes
* Collection types can be represented as any kind of Python object, as long as
  you can convert it to and from a list or dict with string keys.
* Variant records permit fields that accept multiple types of data, permitting
  extensibility.  Variants with default types allow this to be added at any
  point in development (and even permits for *versioned* data models).


Todo/Roadmap
------------
1. Optional native support for numpy arrays
2. No dependency on typing library (use type stubs only)
3. Debug tools for destructure/restructure failures
4. Wrappers around ``attr.s`` and ``attr.ib`` to make defining models cleaner
