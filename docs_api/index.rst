mkdocs-exam API Documentation
==============================

Welcome to mkdocs-exam's API documentation!

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Overview
--------

The mkdocs-exam plugin allows you to create interactive training exams directly in your MkDocs documentation using YAML-based syntax.

Features
--------

- **Multiple Exam Types**: choice, true/false, short-answer, fill-in-the-blank, essay, matching, numeric, code-completion, ordering, categorization, and hotspot
- **Rich Features**: hints with penalties, explanations, media (images/video/audio), time limits, partial credit
- **State Persistence**: Automatic save/restore of exam progress via localStorage
- **Security**: XSS prevention with HTML escaping throughout
- **Modern Architecture**: Type-safe, well-tested, zero technical debt

Quick Start
-----------

1. Install the plugin::

    pip install mkdocs-exam

2. Add to your ``mkdocs.yml``::

    plugins:
      - mkdocs-exam

3. Create an exam in your markdown::

    ```yaml
    question: "What is 2 + 2?"
    answer-correct:
      - "4"
    answer:
      - "3"
      - "5"
    ```

Configuration
-------------

The plugin supports the following configuration options in ``mkdocs.yml``::

    plugins:
      - mkdocs-exam:
          enabled: true                  # Enable/disable plugin
          default_type: choice           # Default exam type
          default_points: 1              # Default points per exam
          show_answers: false            # Show correct answers
          randomize_answers: false       # Randomize answer order
          theme: default                 # Theme: default, minimal, accessible
          strict_validation: false       # Strict error handling

API Reference
-------------

.. toctree::
   :maxdepth: 2

   plugin
   exam_config
   processors
   html_builders

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
