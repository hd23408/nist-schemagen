"""Test methods for testing the schemagen package (specifically,
the SchemaGenerator class).

  Typical usage example:

  python -m unittest

  or, to run a single test:

  python -m unittest -k test__build_schema
"""
import unittest
import pathlib
import logging
import os
import pandas
import schemagen

# Sample files for testing
INVALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/invalid_input_data.csv"))
EMPTY_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/empty_input_data.csv"))
VALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/valid_input_data.csv"))
VALID_SCHEMA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/parameters.json"))

# Test dataframes to convert to a schema. This should contain
# an assortment of the different types that we expect to parse:
# A - int8 numeric categorical
# B - int32 numeric range
# C - string categorical
#
VALID_TEST_DATAFRAME = pandas.DataFrame(
  {
   "A": [1, 2, 3, 4, 5] * 10,
   "B": list(range(1000000, 1000050, 1))
  }
)
# This isn't really a dataframe, it's a dict
INVALID_TEST_DATAFRAME = {
   "A": ["a", "b", "c", "d", "e", "f", "g"],
   "B": list(range(1, 8, 1))
  }

# The appropriate schema and column datatypes to create from the test data above
VALID_TEST_SCHEMA = {
 "schema": {
  "A": {
   "dtype": "uint8",
   "kind": "categorical",
   "values": [ 1, 2, 3, 4, 5 ]
  },
  "B": {
   "dtype": "uint32",
   "kind": "numeric",
   "min": 1000000,
   "max": 1000049
  }
 }
}
VALID_TEST_COLUMN_DATATYPES = {
 "dtype": {
  "A": "uint8",
  "B": "uint32"
 }
}

# Suppress log messages so they don't confuse readers of the test output
logging.basicConfig(level=os.environ.get("LOGLEVEL", "CRITICAL"))

class TestSchemaGenerator(unittest.TestCase):
  """Test class for the schemagen.SchemaGenerator class.
  """

  def test_ctor(self):
    """
    Test that a SchemaGenerator can be appropriately
    instantiated, and that it initializes its internal variables
    appropriately.
    """
    schema_generator = schemagen.SchemaGenerator()
    self.assertIs(type(schema_generator), schemagen.SchemaGenerator)
    self.assertIs(schema_generator.input_csv_file, None)
    self.assertIs(schema_generator.input_data_as_dataframe, None)
    self.assertIs(schema_generator.output_schema, None)

  def test_read_and_parse_csv(self):
    """
    Test the full process of reading in and parsing a CSV file.
    Make sure the `SchemaGenerator.read_and_parse_csv` method
    returns True or False depending on whether it succeeded.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that attempting to parse an invalid file results in "False"
    result = schema_generator.read_and_parse_csv(INVALID_INPUT_DATA_FILE)
    self.assertIs(result, False)

    # Confirm that a valid CSV loads successfully
    result = schema_generator.read_and_parse_csv(VALID_INPUT_DATA_FILE)
    self.assertIs(result, True)

  def test__load_csv_succeeds(self):
    """
    Test that the `SchemaGenerator._load_csv` method can be used to read
    in an appropriately formatted CSV file.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that a valid CSV loads into a DataFrame without throwing errors
    result = schema_generator._load_csv(VALID_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access
    self.assertIsInstance(result, pandas.core.frame.DataFrame)

  def test__load_csv_fails(self):
    """
    Test that the `SchemaGenerator._load_csv` method fails when
    it tries to read a badly formatted CSV or is given an empty
    filename.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that the FileNotFoundError is raised for a non-existing file
    with self.assertRaises(FileNotFoundError):
      schema_generator._load_csv("") # We want to test private methods... pylint: disable=protected-access
    # Confirm that the ParserError is raised when it can't parse the file
    with self.assertRaises(pandas.errors.ParserError):
      schema_generator._load_csv(INVALID_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access
    # Confirm that the EmptyDataError is raised if called against an empty file
    with self.assertRaises(pandas.errors.EmptyDataError):
      schema_generator._load_csv(EMPTY_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access

  def test__build_schema_succeeds(self):
    """
    Test that the `SchemaGenerator._build_schema` method can build
    an expected schema from a properly formatted DataFrame.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that when we build schema off of our test dataframe,
    # we get a result that looks like our expected schema
    (params, columns) = schema_generator._build_schema(VALID_TEST_DATAFRAME) # We want to test private methods... pylint: disable=protected-access
    self.assertEqual(params, VALID_TEST_SCHEMA)
    self.assertEqual(columns, VALID_TEST_COLUMN_DATATYPES)

  def test__build_schema_fails(self):
    """
    Test that the `SchemaGenerator._build_schema` method fails appropriately
    when trying to build a schema from something that is not a DataFrame.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that when we build schema off of our test invalid dataframe,
    # we fail in the right way
    with self.assertRaises(AttributeError):
      schema_generator._build_schema(INVALID_TEST_DATAFRAME, # We want to test private methods... pylint: disable=protected-access
          max_values_for_categorical = 4)

if __name__ == "__main__":
  unittest.main()
