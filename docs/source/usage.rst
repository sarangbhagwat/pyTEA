Usage
=====

.. _installation:

Installation
------------

To use TEAmod, first install it using pip:

.. code-block:: console

   (.venv) $ pip install teamod

Creating a TEA object
---------------------

To create a TEA object,
you can use the ``teamod.TEA`` class:


For example:

>>> import teamod
>>> example_TEA = teamod.TEA(
>>>			     IRR=0.10, # percent as decimal
>>>                	     project_duration=40, # years
>>>                
>>>                	     purchase_cost=10_000_000, # currency
>>>                	     hourly_variable_operating_cost=675, # currency/h
>>>                
>>>                	     hourly_product_flows=[300, 200],
>>>                	     product_prices=[4.2, 1.1],
>>> 
>>> 			     # check the API for a full list of arguments
>>>			)

Solving a TEA
-------------

To solve a tea, you can use either the ``get_NPV_given_IRR`` function, 
or the ``get_IRR_given_NPV function``, or the ``get_MPSP_given_IRR`` function.

For example:

>>> example_TEA.get_IRR_given_NPV(0)

Generating a cash flow report
-------------------------
To obtain and save a cash flow report for your project, you can use the
``get_cashflow_report`` function.

For example:
>>> example_TEA.get_cashflow_report('example_TEA_cashflow_report.xlsx')