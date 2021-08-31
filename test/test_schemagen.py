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
import copy
import os
import pandas as pd
import numpy as np
import schemagen
import filecmp
import string

# Suppress log messages so they don't confuse readers of the test output
logging.basicConfig(level=os.environ.get("LOGLEVEL", "CRITICAL"))

# Sample files for testing
INVALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/invalid_input_data.csv"))
EMPTY_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/empty_input_data.csv"))
VALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/valid_input_data.csv"))
VALID_SCHEMA_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/parameters.json"))

TEST_OUTPUT_DIRECTORY = str(pathlib.Path(__file__).parent.
    joinpath("test_output_files"))
VALID_OUTPUT_PARAMETERS_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/writing_tests/parameters.json"))
VALID_OUTPUT_DATATYPES_FILE = str(pathlib.Path(__file__).parent.
    joinpath("files_for_testing/writing_tests/column_datatypes.json"))

# Test dataframes to convert to a schema. This should contain
# an assortment of the different types that we expect to parse:
# A - float numeric categorical (with missing values)
# B - int32 numeric range
# C - string categorical
#
VALID_TEST_DATAFRAME = pd.DataFrame.from_dict(
  {
    "A": [1, 2, 3, 4, 5, None, None, None, None, None] * 5,
    "B": list(range(1000000, 1000050, 1)),
    "C": ["A", "B", "C", "D", "E"] * 10,
    "D": list(string.ascii_letters)[0 : 50]
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
      "dtype": "float", # This gets turned into a float because of the 'None's
      "kind": "categorical",
      "values": [ 1.0, 2.0, 3.0, 4.0, 5.0 ],
      "codes": [ 1, 2, 3, 4, 5 ]
    },
    "B": {
      "dtype": "uint32",
      "kind": "numeric",
      "min": 999997,
      "max": 1000052,
      "bins": 10
    },
    "C": {
      "dtype": "str",
      "kind": "categorical",
      "values": ["A", "B", "C", "D", "E"],
      "codes": [1, 2, 3, 4, 5]
    },
    "D": {
      "dtype": "str",
      "kind": "text"
    }
  }
}
VALID_TEST_COLUMN_DATATYPES = {
  "dtype": {
    "A": "float",
    "B": "uint32",
    "C": "str",
    "D": "str"
  }
}

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

  def test_output_parameters(self):
    """
    Test outputting of the parameters file.
    """
    schema_generator = schemagen.SchemaGenerator()
    # Make an output directory just for this test
    test_output_dir = pathlib.Path(TEST_OUTPUT_DIRECTORY). \
        joinpath("test_output_parameters")
    test_output_dir.mkdir(parents=True, exist_ok=True)
    test_output_dir = str(test_output_dir)
    test_output_file = str(pathlib.Path(test_output_dir). \
        joinpath("parameters.json"))

    # Set the output schema to a known good values;
    # here we're JUST testing the writing out of the file
    schema_generator.output_schema = copy.deepcopy(VALID_TEST_SCHEMA)

    # Test writing out to a non-existent directory
    retval = schema_generator.output_parameters_json(output_directory="foo")
    self.assertEqual(retval, None)

    # Test success path
    retval = None
    retval = schema_generator.output_parameters_json(output_directory=
        test_output_dir)
    self.assertEqual(retval, test_output_file)
    self.assertTrue(filecmp.cmp(test_output_file, VALID_OUTPUT_PARAMETERS_FILE),
        msg = test_output_file + " does not match " +
        VALID_OUTPUT_PARAMETERS_FILE)


  def test_output_datatypes(self):
    """
    Test outputting of the column_datatypes file.
    """
    schema_generator = schemagen.SchemaGenerator()
    # Make an output directory just for this test
    test_output_dir = pathlib.Path(TEST_OUTPUT_DIRECTORY). \
        joinpath("test_output_datatypes")
    test_output_dir.mkdir(parents=True, exist_ok=True)
    test_output_dir = str(test_output_dir)
    test_output_file = str(pathlib.Path(test_output_dir). \
        joinpath("column_datatypes.json"))

    # Set the output datatypes to a known good values;
    # here we're JUST testing the writing out of the file
    schema_generator.output_datatypes = \
        copy.deepcopy(VALID_TEST_COLUMN_DATATYPES)

    # Test writing out to a non-existent directory
    retval = schema_generator.output_column_datatypes_json(
        output_directory="foo")
    self.assertEqual(retval, None)

    # Test success path
    retval = None
    retval = schema_generator.output_column_datatypes_json(output_directory=
        test_output_dir)
    self.assertEqual(retval, test_output_file)
    self.assertTrue(filecmp.cmp(test_output_file, VALID_OUTPUT_DATATYPES_FILE),
        msg = test_output_file + " does not match " +
        VALID_OUTPUT_DATATYPES_FILE)

  def test__load_csv_succeeds(self):
    """
    Test that the `SchemaGenerator._load_csv` method can be used to read
    in an appropriately formatted CSV file.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that a valid CSV loads into a DataFrame without throwing errors
    result = schema_generator._load_csv(VALID_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access
    self.assertIsInstance(result, pd.core.frame.DataFrame)

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
    with self.assertRaises(pd.errors.ParserError):
      schema_generator._load_csv(INVALID_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access
    # Confirm that the EmptyDataError is raised if called against an empty file
    with self.assertRaises(pd.errors.EmptyDataError):
      schema_generator._load_csv(EMPTY_INPUT_DATA_FILE) # We want to test private methods... pylint: disable=protected-access

  def test__build_schema_succeeds(self):
    """
    Test that the `SchemaGenerator._build_schema` method can build
    an expected schema from a properly formatted DataFrame.
    """
    schema_generator = schemagen.SchemaGenerator()

    # Confirm that when we build schema off of our test dataframe,
    # we get a result that looks like our expected schema
    (params, columns) = schema_generator._build_schema(VALID_TEST_DATAFRAME,
        include_text_columns=True) # We want to test private methods... pylint: disable=protected-access
    self.assertEqual(params, VALID_TEST_SCHEMA)
    self.assertEqual(columns, VALID_TEST_COLUMN_DATATYPES)

    # Confirm that when we build schema off of our test dataframe,
    # and include "na", we get a result that looks like we expect
    (params, columns) = schema_generator._build_schema(VALID_TEST_DATAFRAME, # We want to test private methods... pylint: disable=protected-access
            include_text_columns=True, include_na=True)
    valid_schema_with_nan = copy.deepcopy(VALID_TEST_SCHEMA)
    valid_schema_with_nan["schema"]["A"]["values"].append(np.NaN)
    # Including NaN is going to make everything in the column a float
    valid_schema_with_nan["schema"]["A"]["dtype"] = "float"
    valid_schema_with_nan["schema"]["A"]["values"] = \
        list(map(float, valid_schema_with_nan["schema"]["A"]["values"]))
    valid_schema_with_nan["schema"]["A"]["codes"] = \
        [1, 2, 3, 4, 5, 6]
    valid_dtypes_with_nan = copy.deepcopy(VALID_TEST_COLUMN_DATATYPES)
    valid_dtypes_with_nan["dtype"]["A"] = "float"

    # Need to use np's assertion in order to make NaN == NaN
    np.testing.assert_equal(params, valid_schema_with_nan)
    self.assertEqual(columns, valid_dtypes_with_nan)

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

  def test__getters(self):
    """
    Test that the getters for the output schema and the column datatypes
    return the correct objects.
    """
    schema_generator = schemagen.SchemaGenerator()

    schema_generator.output_schema = copy.deepcopy(VALID_TEST_SCHEMA)
    self.assertEqual(schema_generator.get_parameters_json(),
        VALID_TEST_SCHEMA)

    schema_generator.output_datatypes = \
        copy.deepcopy(VALID_TEST_COLUMN_DATATYPES)
    self.assertEqual(schema_generator.get_column_datatypes_json(),
        VALID_TEST_COLUMN_DATATYPES)

  def test__get_series_dtype(self):
    """
    Test that the method that determines the appropriate datatype, min, and max
    values does the right thing.
    """
    schema_generator = schemagen.SchemaGenerator()

    series = pd.Series(["a", "b", "c", "d"])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("str", None, None))

    series = pd.Series([1, 2, 2, 3, 4, 5, 6, 7, 8, 9])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("uint8", 0, 10))

    series = pd.Series(list(range(1000000, 1000050, 1)))
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("uint32", 999997, 1000052))

    series = pd.Series([0.1, 0.15, 0.2, 0.214, 0.25])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("float", 0.0925, 0.2575))

    series = pd.Series([-1, 0, 1, -2, 0, -3])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("int8", -4, 2))

    # If min is 0, don't "fuzz" it, to avoid going negative
    series = pd.Series([0, 1, 2, 3, 4, 5])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("uint8", 0, 6))

    series = pd.Series(["2021-02-25", "2021-01-05", "2021-06-22"])
    self.assertEqual(schema_generator._get_series_dtype(series), # We want to test private methods... pylint: disable=protected-access
        ("date", "2021-01-05 00:00:00", "2021-06-22 00:00:00"))


if __name__ == "__main__":
  unittest.main()
