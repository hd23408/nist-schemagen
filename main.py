import argparse, logging, os, sys
import schemagen, validate


def generate_schema(input_file):
  # Create a SchemaGenerator
  schema_generator = schemagen.SchemaGenerator()
  
  # TODO: Allow user to specify for max values for categorical
  # TODO: Allow user to specify properties to force into categorical
  
  # Parse the input file
  loading_result = schema_generator.read_and_parse_csv(input_file)
  
  # If the loading was unsuccessful, exit
  if not loading_result:
    logging.error("Unable to load the specified CSV file. Please review logs for details.")
    return None
  
  # TODO: Review the schema and prompt for names for categorical and ranges for numeric
  return schema_generator

def output_schema(schema_generator):
  # TODO: Allow user to specify output directory
  
  # Output the parameters.json file to the output directory (if specified)
  output_parameters_json = schema_generator.output_parameters_json(output_directory = ".")
  output_column_datatypes_json = schema_generator.output_column_datatypes_json(output_directory = ".")
  
  # Validate the output schema 
  logging.info("Done generating schema. Validating output files...")
  try:
    validate.validate_schema(output_parameters_json, True)
  except:
    logging.exception(f"Caught an error when trying to validate {output_parameters_json}:" )
    logging.warning(f"{output_parameters_json} file should be reviewed manually to ensure it is complete.")
  
  try:
    validate.validate_schema(output_column_datatypes_json, False)
  except:
    logging.exception(f"Caught an error when trying to validate {output_column_datatypes_json}:" )
    logging.warning(f"{output_column_datatypes_json} file should be reviewed manually to ensure it is complete.")
  
  print("\nSchema generator is complete! Schema files are:")
  print(output_parameters_json)
  print(output_column_datatypes_json)

if __name__ == '__main__':
  # validate.py executed as script
  # Configure the logger to output everything; logs will
  # go to stderr by default
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
  
  # Set up the argument parser for this helper script 
  parser = argparse.ArgumentParser(description='Create a schema from an input CSV file.')
  parser.add_argument('inputfile', help='The input file to process')
  
  # The argument parser will error out if the input file isn't specified
  args = parser.parse_args()
  schema_generator = generate_schema(args.inputfile)
  if not schema_generator:
    sys.exit()
  output_schema(schema_generator)
