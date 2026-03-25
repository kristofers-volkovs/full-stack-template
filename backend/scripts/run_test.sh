#!/bin/bash

coverage run --source=tests -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"
