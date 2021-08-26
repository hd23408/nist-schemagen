"""A script to run the schema generator against a CSV file.

TODO: Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  python main.py my_input_file.csv
"""

import argparse
import logging
import os
import sys
import schemagen
import validate


def generate_schema(input_file):
  # Create a SchemaGenerator
  local_schema_generator = schemagen.SchemaGenerator()

  # TODO: Allow user to specify for max values for categorical
  # TODO: Allow user to specify properties to force into categorical

  # Parse the input file
  loading_result = local_schema_generator.read_and_parse_csv(input_file)

  # If the loading was unsuccessful, exit
  if not loading_result:
    logging.error("Unable to load the specified CSV file.")
    return None

  # TODO: Review the schema and prompt for names and ranges
  return local_schema_generator

def output_schema(param_schema_generator):
  # TODO: Allow user to specify output directory

  # Output the parameters.json file to the output directory (if specified)
  output_parameters_json = param_schema_generator.output_parameters_json(
      output_directory = "."
  )
  output_column_datatypes_json = \
      param_schema_generator.output_column_datatypes_json(
          output_directory = "."
      )

  # Validate the output schema
  logging.info("Done generating schema. Validating output files...")
  try:
    validate.validate_schema(output_parameters_json, True)
  except: # Logging the full exception... pylint: disable=bare-except
    logging.exception("Caught an error when trying to validate %s",
        output_parameters_json)
    logging.warning("%s file should be reviewed to ensure it is complete.",
        output_parameters_json)

  try:
    validate.validate_schema(output_column_datatypes_json, False)
  except: # Logging the full exception... pylint: disable=bare-except
    logging.exception("Caught an error when trying to validate %s",
        output_column_datatypes_json)
    logging.warning("%s should be reviewed manually to ensure it is complete.",
        output_column_datatypes_json)

  print("\nSchema generator is complete! Schema files are:")
  print(output_parameters_json)
  print(output_column_datatypes_json)

if __name__ == "__main__":
  # validate.py executed as script
  # Configure the logger to output everything; logs will
  # go to stderr by default
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

  # Set up the argument parser for this helper script
  parser = argparse.ArgumentParser(
          description="Create a schema from an input CSV file."
  )
  parser.add_argument("inputfile", help="The input file to process")

  # The argument parser will error out if the input file isn't specified
  args = parser.parse_args()
  schema_generator = generate_schema(args.inputfile)
  if not schema_generator:
    sys.exit()
  output_schema(schema_generator)
