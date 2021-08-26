#!/bin/bash

echo "main.py"
pylint main.py
echo "validate.py"
pylint validate.py
echo "schemagen/"
pylint schemagen
echo "test/"
pylint test
