#!/bin/bash

python -c "import src.main.app; import json; print(json.dumps(src.main.app.server.openapi()))" > src/openapi.json
python ./scripts/cleanup_openapi_schema.py
