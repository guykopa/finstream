finstream
=========

Industrial ETL pipeline for financial data processing.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   overview
   architecture
   api_reference
   cli

Overview
--------

finstream covers the full data lifecycle of a Finance Information System:

- **Extract** financial transactions from PostgreSQL, CSV files, or REST APIs
- **Transform** data: currency normalisation, deduplication, date standardisation
- **Validate** data quality with a 5-rule engine and configurable quality gate
- **Load** clean data into PostgreSQL with chunk-based Big Data processing
- **Expose** pipeline triggers and metrics via a secured FastAPI REST API (JWT)
- **Monitor** production with Prometheus metrics, structured JSON logs, and Grafana

Quick Start
-----------

.. code-block:: bash

   # Install dependencies
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt

   # Set required environment variable
   export JWT_SECRET="your-secret-key-minimum-32-chars"

   # Run the API
   uvicorn finstream.api.main:app --reload

   # Run the pipeline via CLI
   python -m finstream.cli.cli run --date 2024-01-15 --source fake

   # Run tests
   pytest tests/

API Reference
-------------

.. automodule:: finstream.interfaces.i_data_source
   :members:

.. automodule:: finstream.interfaces.i_transformer
   :members:

.. automodule:: finstream.interfaces.i_quality_rule
   :members:

.. automodule:: finstream.domain.models.transaction
   :members:

.. automodule:: finstream.domain.models.pipeline_report
   :members:

.. automodule:: finstream.quality.quality_engine
   :members:

.. automodule:: finstream.domain.services.etl_service
   :members:

.. automodule:: finstream.pipeline.etl_pipeline
   :members:
