"""This is module for the SchemaGenerator class, which is used
to create schema files based on an existing CSV file.

The schema generator takes as input a comma-separated datafile.
The output is two files, a `parameters.json` file and a
`column_datatypes.json` file. These files can be written
out using the output_prarmeters_json and output_column_datatypes_json
methods.

  Typical usage example:

  schema_generator = schemagen.SchemaGenerator()
  input_file = "/path/to/file.csv"
  schema_generator.read_and_parse_csv(input_file)
  parameters_json = schema_generator.get_parameters_json()
"""

import os.path
import json
import logging
import pandas as pd
import numpy as np

DEFAULT_MAX_VALUES_FOR_CATEGORICAL = 25
DEFAULT_INCLUDE_NA = False
NAME_FOR_PARAMETERS_FILE = "parameters.json"
NAME_FOR_DATATYPES_FILE = "column_datatypes.json"

class SchemaGenerator:
  """This is a schema generating class. It can be used to read an input
  comma-separated values file and infer a schema (including datatypes,
  categorical values, and ranges).

  The schema generator takes as input a comma-separated datafile.
  The output is two files, a `parameters.json` file and a
  `column_datatypes.json` file. These files can be written
  out using the output_prarmeters_json and output_column_datatypes_json
  methods.

  The `parameters.json` file contains detailed information about each
  column, and will conform to the
  :download:`parameters.json.schema <../../json_schemae/parameters.json.schema>`
  The `column_datatypes.json` file just contains the datatype information
  for each column in order to make processing easier, and will conform to the
  :download:`column_datatypes.json.schema <../../json_schemae/column_datatypes.json.schema>`. # Links on the same line make sphinx happy... pylint: disable=line-too-long

  """

  def __init__(self):
    """This method creates a new SchemaGenerator.
    The SchemaGenerator can then be used by calling
    the load_csv method to read in a CSV file, and
    the output methods to output the generated schema.
    """
    # Initialize class variables
    self._clear_class_variables()

    # Set up a logger for this module
    self.log = logging.getLogger(__name__)

  def read_and_parse_csv(self, input_csv_file):
    """This method loads in a new input CSV file and attempts to infer
    a schema from it. If the SchemaGenerator has already been used to
    generate a schema from a different input file, this method will clear
    out the previous schema (even if it encounters an error when
    reading in a new file). (If it is desirable to keep multiple schemae,
    a different SchemaGenerator should be used for each input file.)

    Error-handling: This method will trap and log exceptions directly,
    and return a simple bool indicating success or failure. To configure
    how this method logs, use the ...

    :param input_csv_file: the CSV file that should be examined to determine the
    schema
    :type input_csv_file: str

    :return: whether or not the loading was successful
    :rtype: bool
    """

    #TODO:
    # - how to configure logging
    # - allow specifying max values for categorical

    # Since we're reading in a new input file, first we should
    # re-initialize the output schema that we'll be generating
    # from it. Additionally, clear out the dataframe that
    # is being used to generate the schema, and the local
    # tracking variable for the name of the CSV file.
    self._clear_class_variables()

    # Set the local input_csv_file variable, just to track
    # the file that we're reading in.
    self.input_csv_file = input_csv_file

    # Read the file into the local dataframe
    try:
      self.input_data_as_dataframe = self._load_csv(self.input_csv_file)
    except: # Logging the full exception... pylint: disable=bare-except
      # Re-clear these variables to make sure nothing is in a half-loaded state
      self._clear_class_variables()

      self.log.exception("Caught an error when trying to load input file:" )
      return False

    try:
      # Do the processing needed to generate the schema
      (self.output_schema, self.output_datatypes) = \
            self._build_schema(self.input_data_as_dataframe)
    except: # Logging the full exception... pylint: disable=bare-except
      # Re-clear these variables to make sure nothing is in a half-loaded state
      self._clear_class_variables()

      self.log.exception("Caught an error when trying to parse schema:" )
      return False

    return True

  def get_parameters_json(self):
    """Returns the content that would be written to the `parameters.json` file
    as a Python dict. This contains full information about the different
    properties in the input CSV file that was parsed by the SchemaGenerator.
    It will conform to the
    :download:`parameters.json.schema <../../json_schemae/parameters.json.schema>` # Links on the same line make sphinx happy... pylint: disable=line-too-long
    JSON schema. Returns None if no file has been parsed, or if the most recent
    file was unable to be parsed.

    :return: a Python dict that contains the `parameters.json` content.
    :rtype: dict
    """
    return self.output_schema

  def output_parameters_json(self, output_directory = "."):
    """This method outputs the `parameters.json` file into
    the specified directory. The `parameters.json` file
    contains information about each column in the file, including
    min/max, values, and/or datatype. This file is expected to conform to the
    :download:`parameters.json.schema <../../json_schemae/parameters.json.schema>` # Links on the same line make sphinx happy... pylint: disable=line-too-long
    JSON schema.

    :param output_directory: (optional) the directory into which to output the
    file. If not specified, will write out to the current working directory.
    :type output_directory: str

    :return: full filepath to the output file
    :rtype: str
    """

    #TODO:
    # - try/catch writing out the file

    output_file = os.path.join(output_directory, NAME_FOR_PARAMETERS_FILE)

    self.log.info("Writing output parameters file %s...", output_file)

    with open(output_file, "w", encoding="utf-8") as write_file:
      json.dump(self.output_schema, write_file, indent=2)

    self.log.info("Done writing output parameters file.")
    return output_file

  def output_column_datatypes_json(self, output_directory = "."):
    """This method outputs the `column_datatypes.json` file into
    the specified directory. The `column_datatypes.json` file
    contains a JSON object that identifies just the datatype
    of each column. It also includes a `skipinitialspace` property
    that can be set to true or false.

    :param output_directory: (optional) the directory into which to output the
    file. If not specified, will write out to the current working directory.
    :type output_directory: str

    :return: full filepath to the output file
    :rtype: str
    """

    #TODO:
    # - what is the skipinitialspace property?
    # - try/catch writing out the file

    output_file = os.path.join(output_directory, NAME_FOR_DATATYPES_FILE)
    self.log.info("Writing output column datatypes file %s...", output_file)

    with open(output_file, "w", encoding="utf-8") as write_file:
      json.dump(self.output_datatypes, write_file, indent=2)

    self.log.info("Done writing output column datatypes file.")

    return output_file

  # PRIVATE METHODS BELOW HERE
  def _clear_class_variables(self):
    """This method just clears out the class
    variables, and resets the SchemaGenerator to
    its pristine state.
    """
    self.output_schema = None
    self.output_datatypes = None
    self.input_data_as_dataframe = None
    self.input_csv_file = None

  def _load_csv(self, input_csv_file):
    """
    Loads in the CSV file as a pandas DataFrame

    :param input_csv_file: the CSV file that should be examined to determine
    the schema
    :type input_csv_file: str

    :return: The input CSV file as a dataframe (will raise exceptions if it
    encounters them)
    :rtype: pandas.DataFrame
    """

    self.log.info("Reading CSV file...")

    # Set a default return value
    input_data_as_dataframe = None

    # Read in the input file with pandas. If this fails,
    # throw an error and get out.
    try:
      input_data_as_dataframe = pd.read_csv(input_csv_file)
    except pd.errors.ParserError as err:
      # This is likely to be a common error, so check for it explicitly
      self.log.error("Using input file: '%s', \
          'pandas.read_csv()' was unable to parse the input file \
          as a CSV. Please confirm that it contains valid comma-separated \
          values.", input_csv_file)
      raise err
    except FileNotFoundError as err:
      # This is likely to be a common error, so check for it explicitly
      self.log.error("Using input file: '%s', \
          the file was not found. Please confirm the specified \
          path, or use a full path instead of a relative path.", input_csv_file)
      raise err
    except pd.errors.EmptyDataError as err:
      # This is likely to be a common error, so check for it explicitly
      self.log.error("\nUsing input file: '%s', \
          The file appears to be empty. Please confirm the path.",
          input_csv_file)
      raise err
    except BaseException as err:
      # An error was thrown that we weren't expecting; log and rethrow to caller
      self.log.error("\nUsing input file: '%s', \
          The system received an unexpected error when trying to \
          parse the input file using 'pandas.read_csv()'.", input_csv_file)
      raise err

    self.log.info("Successfully read CSV file.")

    return input_data_as_dataframe


  def _build_schema(self, input_data_as_dataframe,
            max_values_for_categorical = DEFAULT_MAX_VALUES_FOR_CATEGORICAL,
            include_na = DEFAULT_INCLUDE_NA):
    """This method contains the business logic to build an appropriate
    schema object based on the information from the input dataset. It uses
    numpy helper functions to figure out what the appropriate datatype should
    be, and uses pandas to determine unique values for categorical datatypes.

    This method determines whether a numeric variable is categorical or not by
    comparing the number of values in the file to max_values_for_categorical
    parameter. This parameter defaults to `DEFAULT_MAX_VALUES_FOR_CATEGORICAL`.

    The method can also optionally include "NaN" as a value for categorical
    variables that contain some rows that do not have values. By default, it
    will not include NaN as a possible value.

    Note that if the input dataset has duplicate column names, they will be
    named as "column", "column.1", "column.2", etc. in the output schema.
    This is how the `pandas` package handles duplicate column names, and since
    we expect that most people who are using this module will also be using
    pandas, it seems reasonable to keep this behavior.

    :param input_data_as_dataframe: a pandas DataFrame that should be examined
        to determine the schema
    :type input_data_as_dataframe: pandas.DataFrame
    :param max_values_for_categorical: columns with fewer than this many values
        will be considered categorical
    :type max_values_for_categorical: number
    :param include_na: whether or not to include `NaN` as a value for
        categorical fields
    :type include_na: bool

    :return: tuple of dicts representing the full schema and the column
        datatypes, respectively
    :rtype: tuple
    """


    if include_na:
      self.log.info("Building schema...")
    else:
      self.log.info("Building schema without using NAs...")

    # Start the return value off with an empty schema structure
    output_schema = { "schema": {} }
    output_datatypes = { "dtype": {} }

    # loop over each column, and add the values and the datatype to the dict
    for column in input_data_as_dataframe.columns:

      # The actual values for the column
      series = input_data_as_dataframe[column]
      if not include_na:
        self.log.info("Removing NA values from column %s", column)
        series.dropna(inplace=True)

      # Local variable to store the schema for this particular column
      col_schema = {}

      # Unique values for this column
      values = pd.unique(series)
      (datatype, min_value, max_value) = self._get_series_dtype(series)
      col_schema["dtype"] = datatype

      # Now, decide if this should be treated as a categorical value or
      # something else, by checking to see how many unique values
      # there are.
      if len(values) <= max_values_for_categorical:
        # Treat as a categorical value and output a list of unique values
        col_schema["kind"] = "categorical"
        try:
          values.sort()
        except: # Logging the full exception... pylint: disable=bare-except
          self.log.exception("Encountered an error when trying to sort the \
                values. Will include them without sorting.")
        col_schema["values"] = values.tolist()

      else:
        if col_schema["dtype"] == "str":
          self.log.warning("\nNot using values for column '%s' \
            because it is non-numeric and there are more than %s \
            unique values for it. This column will be labeled as an \
            ID-type string, and values will not be included.",
            str(column), str(max_values_for_categorical))
          col_schema["kind"] = "id"
        elif col_schema["dtype"] == "date":
          col_schema["kind"] = "date"
          col_schema["min"] = min_value
          col_schema["max"] = max_value
        else:
          # Treat it as a numeric value.
          col_schema["kind"] = "numeric"
          col_schema["min"] = min_value
          col_schema["max"] = max_value

      output_schema["schema"][column] = col_schema
      # Also add this column and its datatype to the output_datatypes dict
      output_datatypes["dtype"][column] = col_schema["dtype"]

    self.log.info("Schema building successful.")
    return (output_schema, output_datatypes)


  def _get_series_dtype(self, series):
    """
    Determine the datatype that we want to put into our schema files. This isn't
    necessarily the same as what pandas thinks the datatype of the column is.
    Additionally, for numeric or datetime columns, determine the min/max values
    for the column (since we're examining the column anyway).

    :param: series a pandas series to examine
    :type: pandas.series

    :return: a tuple containing the string version of the datatype to use and,
        if relevant, min and max values
    :rtype: str
    """

    # default datatype value is "str" when all else fails
    datatype = "str"
    # default min/max are just None
    min_value = None
    max_value = None

    if series.dtype.kind in ['i', 'u']: # pylint: disable=inconsistent-quotes
      # If we believe the datatype is an int, we want to
      # figure out the smallest numpy datatype that can store
      # it, given the min and max values
      min_value = series.min().item()
      max_value = series.max().item()

      # Determine the smallest type that will work for both the min
      # and the max value (need to do both min and max because of
      # signed vs. unsigned integers)
      smallest_type = np.promote_types(np.min_scalar_type(min_value),
            np.min_scalar_type(max_value))
      # That's the type we'll put in the schema
      datatype = smallest_type.name
      min_value = series.min().item()
      max_value = series.max().item()

    elif series.dtype.kind in ['f', 'c']: # pylint: disable=inconsistent-quotes
      # numpy dtypes will be `float32`/`float64`, but we just want `float`.
      # This is a bit of a hack to get the base name of the datatype and
      # should work for things that aren't floats, too, just in case.
      # See also https://stackoverflow.com/a/9453240
      datatype = type(np.zeros(1,series.dtype).tolist()[0]).__name__

    else:
      # See if we can parse it as a date
      try:
        dt = pd.to_datetime(series)
        datatype = "date"
      except: # Logging the full exception... pylint: disable=bare-except
        # Default to it just being a string
        datatype = "str"
      else:
        min_value = str(dt.min())
        max_value = str(dt.max())

    return (datatype, min_value, max_value)
