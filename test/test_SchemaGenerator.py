import unittest, pathlib, logging, os, json
import pandas, schemaGen

# Sample files for testing
INVALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.joinpath("files_for_testing/invalid_input_data.csv"))
EMPTY_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.joinpath("files_for_testing/empty_input_data.csv"))
VALID_INPUT_DATA_FILE = str(pathlib.Path(__file__).parent.joinpath("files_for_testing/valid_input_data.csv"))
VALID_SCHEMA_FILE = str(pathlib.Path(__file__).parent.joinpath("files_for_testing/parameters.json"))

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
# This dataframe is used to test to make sure we appropriately
# skip columns with too many non-numeric values
INVALID_TEST_DATAFRAME_NONNUMERIC = pandas.DataFrame(
        {
            "A": ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
            "B": list(range(1, 8, 1))
        }
)
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

# Suppress log messages so they don't confuse readers of the test output
#logging.basicConfig(level=os.environ.get("LOGLEVEL", "CRITICAL"))

class TestSchemaGenerator(unittest.TestCase):

    def test_ctor(self):
        """
        Test to make sure that a SchemaGenerator can be appropriately
        instantiated and that it initializes its internal variables.
        """
        schema_generator = schemaGen.SchemaGenerator()
        self.assertIs(type(schema_generator), schemaGen.SchemaGenerator)
        self.assertIs(schema_generator.input_csv_file, None)
        self.assertIs(schema_generator.input_data_as_dataframe, None)
        self.assertIs(schema_generator.output_schema, None)

    def test_read_and_parse_csv(self):
        """
        Test the full process of reading in and parsing a CSV file.
        Make sure it returns True or False depending on whether it succeeded.
        """
        schema_generator = schemaGen.SchemaGenerator()

        # Confirm that attempting to parse an invalid file results in a "False" retval
        result = schema_generator.read_and_parse_csv(INVALID_INPUT_DATA_FILE)
        self.assertIs(result, False)

        # Confirm that a valid CSV loads successfully
        result = schema_generator.read_and_parse_csv(VALID_INPUT_DATA_FILE)
        self.assertIs(result, True)

    def test__load_csv_succeeds(self):
        """
        Test to make sure that a SchemaGenerator can be used to load
        in an appropriately formatted CSV.
        """
        schema_generator = schemaGen.SchemaGenerator()

        # Confirm that a valid CSV loads into a DataFrame without throwing errors
        result = schema_generator._load_csv(VALID_INPUT_DATA_FILE)
        self.assertIsInstance(result, pandas.core.frame.DataFrame)

    def test__load_csv_fails(self):
        """
        Test to make sure that a SchemaGenerator fails when
        it tries to read a badly formatted CSV or is given an empty
        filename.
        """
        schema_generator = schemaGen.SchemaGenerator()

        # Confirm that the FileNotFoundError is raised if called against a non-existing file
        with self.assertRaises(FileNotFoundError):
            result = schema_generator._load_csv("")
        # Confirm that the ParserError is raised when it can't parse the file
        with self.assertRaises(pandas.errors.ParserError):
            result = schema_generator._load_csv(INVALID_INPUT_DATA_FILE)
        # Confirm that the EmptyDataError is raised if called against an empty file
        with self.assertRaises(pandas.errors.EmptyDataError):
            result = schema_generator._load_csv(EMPTY_INPUT_DATA_FILE)

    def test__build_schema_succeeds(self):
        """
        Test to make sure that a SchemaGenerator can build a schema
        from a properly formatted DataFrame.
        """
        schema_generator = schemaGen.SchemaGenerator()

        # Confirm that when we build schema off of our test dataframe,
        # we get a result that looks like our expected schema
        result = schema_generator._build_schema(VALID_TEST_DATAFRAME)
        self.assertEqual(result, VALID_TEST_SCHEMA)

    def test__build_schema_fails(self):
        """
        Test to make sure that a SchemaGenerator fails appropriately
        when trying to build a schema from an improperly formatted
        DataFrame.
        """
        schema_generator = schemaGen.SchemaGenerator()

        # Confirm that when we build schema off of our test invalid dataframe,
        # we fail in the expected way
        result = schema_generator._build_schema(INVALID_TEST_DATAFRAME_NONNUMERIC, max_values_for_categorical = 4)
        #self.assertEqual(result, VALID_TEST_SCHEMA)
        print(result)


if __name__ == '__main__':
    unittest.main()
