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
import json

def generate_schema(input_file, max_categorical, include_na):
  # Create a SchemaGenerator
  local_schema_generator = schemagen.SchemaGenerator()

  # TODO: Allow user to specify properties to force into categorical

  # Parse the input file
  loading_result = local_schema_generator.read_and_parse_csv(input_file,
    max_categorical, include_na)

  # If the loading was unsuccessful, exit
  if not loading_result:
    logging.error("Unable to load the specified CSV file.")
    return None

  return local_schema_generator

def output_schema(param_schema_generator, output_dir):
  # Output the parameters.json file to the output directory (if specified)
  output_parameters_json = param_schema_generator.output_parameters_json(
      output_directory = output_dir
  )
  output_column_datatypes_json = \
      param_schema_generator.output_column_datatypes_json(
          output_directory = output_dir
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

def review_schema(param_schema_generator):
  schema = param_schema_generator.get_parameters_json()
  for column in schema["schema"]:
    print("--------")
    print(f"For column '{column}', the schema generator has inferred:")
    print(json.dumps(schema["schema"][column], indent=4, sort_keys=True))
    user_input = ""
    while user_input.lower() not in ["y","n"]:
      user_input = str(input("Does this look correct? y/n "))
    # TODO: Allow reviewing of the input

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

  parser.add_argument("-o", "--outputdir", help=
    "The output directory for the generated files. Defaults to the\
    current working directory", default=".")

  parser.add_argument("-m", "--max_categorical", help=
    "The maximum number of unique values allowed to be considered categorical. \
    Must be an integer. Defaults to " +
    str(schemagen.DEFAULT_MAX_VALUES_FOR_CATEGORICAL),
    default=schemagen.DEFAULT_MAX_VALUES_FOR_CATEGORICAL, type=int)

  parser.add_argument("-i", "--include_na", help=
    "Whether or not to include NA as part of the categorical values, if some \
    records don't have a value for that column. Defaults to " +
    str(schemagen.DEFAULT_INCLUDE_NA),
    default=schemagen.DEFAULT_INCLUDE_NA, action="store_true")

  parser.add_argument("-r", "--review_schema", help=
    "Whether or not to review each column individually as part of this \
    script. Defaults to False", default=False, action="store_true")

  # The argument parser will error out if the input file isn't specified
  args = parser.parse_args()

  # Generate the schema
  schema_generator = generate_schema(args.inputfile,
          args.max_categorical, args.include_na)

  # The schema wasn't able to be generated
  if not schema_generator:
    logging.error("Unable to generate schema. Please review logs for details.")
    sys.exit()

  # If desired, allow the user to review the schema column by column
  if args.review_schema:
    review_schema(schema_generator)

  # Output the schema files
  output_schema(schema_generator, args.outputdir)

