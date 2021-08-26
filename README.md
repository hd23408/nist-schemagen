# Schema Generator
This repository contains a simple "schema generator" that will use the data
from an input CSV to infer its schema. This is primarily intended for use by the
teams participating in the [NIST 2020 differential privacy challenge](https://www.nist.gov/ctl/pscr/open-innovation-prize-challenges/current-and-upcoming-prize-challenges/2020-differential),
as the resulting schema that gets generated by this tool mimics the schemae
that were used for their challenge datasets. Teams (or others!) are welcome to
include this module in their final projects or link to it on [github]().

## Assertions
This tool assumes that the schema is learnable from the input dataset, and
specifically that all categorical values are included in the input (and
therefore can be inferred by this tool).

Note that this approach of taking the schema from the input data is generally
considered to be "cheating" when it comes to differential privacy! However,
in a real world context and when attempting to make something that's as easy
for researchers to use as possible, learning the schema from the input data is
often justified.

## When Not to Use This Tool
Do not use this tool in situations where the input data is sparse enough that
values that should be in the schema don’t actually occur in the data, or if
there are hundreds of possible categorical values and some values aren’t
included in the data. Additionally, don't use this tool if reading values from
the input data itself could be considered a breach of privacy, or if generating
a schema from those values would reveal information about the data that should
be kept private.

## Input File
The input file for this tool must meet the following requirements:

* It must be a CSV
* The first row must be a header row
* Each row should consist of the same number of columns as the header row
(although rows may have blank or missing values for a given column)

## Output Produced
The output will be two files (and/or Python dicts, if using as a module):

* `parameters.json`, which contains information such as datatype (`dtype`),
plus a list of acceptable values (for categorical variables) or a min/max and
optional binning information (for numeric variables)
* `column_datatypes.json`, which contains a list of all the columns and
their datatypes

These files will be formatted according to the JSON schemae provided in this
tool's `json_schemae` directory, and can be validated using the validation tool
provided (see below).

### Example Output:

These examples were created from an input file that looked something like like this:

```
ID,Age,Date,State
A-123,14,2012-01-01,CA
B-526,22,2014-06-09,CT
C-9725,87,2020-12-31,TX
...
```

#### parameters.json
```
{
  "schema": {
    "ID": {
      "dtype": "str",
      "kind": "id"
    },
    "Age": {
      "dtype": "uint8",
      "kind": "numeric",
      "min": 14,
      "max": 87
    },
    "Date": {
      "dtype": "date",
      "kind": "date",
      "min": "2012-01-01 00:00:00",
      "max": "2020-12-31 00:00:00"
    },
    "State": {
      "dtype": "str",
      "kind": "categorical",
      "values": [
        "CA",
        "CT",
        "FL",
        "TX"
      ]
    }
  }
}
```

#### column_datatypes.json
```
{
  "dtype": {
    "ID": "str",
    "Age": "uint8",
    "Date": "date",
    "State": "str"
  }
}
```

# Using the Tool

## Dependencies
This tool requires Python version 3.9 or above.

The `requirements.txt` file in the root directory contains information about
the modules that this tool depends on.

### Virtual Environment
**It is strongly recommended that you use a Python virtual environment.**
If you are not familiar with Python virtual environments, [this]
(https://docs.python.org/3/library/venv.html) is a good place to start.
(If you do not wish to use a virtual environment, you can jump straight to
step 3 below.)

1. To create a virtual environment (this only needs to be done once), run
the following from the root directory of this project:
`python3 -m venv .env`

2. Then, any time you want to work on the project, start by activating
the virtual environment. Full instructions for different platforms
can be found
[in the python documentation](https://docs.python.org/3/library/venv.html),
but in general it will be some variation (depending on your platform) on
`source .env/bin/activate` (do this whenver you open a new command prompt
and want to work with this project)

3. Once you have created and activated a virtual environment, you can install
the requirements: `pip install -r requirements.txt` (do this only once)

## Generating a Schema

### Approach
The schema generator acts on the assumption that the provided datafile
contains at least one record for every possible value for categorical variables.
It will determine the datatype and, if relevant, build a list of acceptable
values by looking at this set of data. When run from a command line, it can
also prompt the user to review the generated schema and correct any situations
where its inferences were incorrect.

### Running From the Command Line
To run the tool from a command line, do the following:

1. (if using a virtual environment) Activate your venv (if you haven't already):
`source .env/bin/activate` (or a variation depending on your platform, see above)

2. Run the tool using its defaults:
`python main.py /path/to/input.csv`

3. After the tool has processed your input CSV file, two files will be written
out directly in the root directory:
	* `parameters.json` 
	* `column_datatypes.json`

#### Command-Line Arguments
The script provides a variety of command-line options, which can be 
viewed by running `python main.py -h`. They are:

* `-o, --output_dir`: an output directory into which the output files should be
written (e.g. `python main.py -o /path/to/output /path/to/input.csv`)
* `-m, --max_categorical`: the maximum number of values a column can have
to be considered categorical. Columns with more than this number of values will
be treated as ranges. Defaults to 25.
* `-i, --include_na`: Whether or not to include "NaN" as one of the categorical
values, when there are some rows that don't have a value for that column. Defaults
to False.


### Using as a Module
The tool can also be used as a module within a larger program. For details,
please refer to the documentation available [here](https://hd23408.github.io/nist-schemagen/html/schemagen.html)
(TODO: Put this documentation somewhere that will allow it to use the sphinx theme)

In brief:

```
import schemagen
schema_generator = schemagen.SchemaGenerator()
input_file = "/path/to/file.csv"
schema_generator.read_and_parse_csv(input_file)
parameters_json = schema_generator.get_parameters_json()
```

# Validating an Existing Schema
This tool can also be used to validate an existing schema file that was produced
either by this tool or by hand. When running the tool from the command line,
the produced schema files will be validated for you, but you can also run
with the following (after activating your venv, if using one):

`python validate.py -p output/parameters.json`

or

`python validate.py -d output/column_datatypes.json`

The validator will check the format of the file against the associated
JSON schema file and report any issues. It can be used to check the
validity of schema files produced by this tool or produced by hand.

# Running Tests
To run tests, from the main project directory do the following
(after activating your venv, if using one):

To run all tests:

`python -m unittest`

To run a single test:

`python -m unittest -k test__build_schema` (or other test name)

# Running PyLint
This code attempts to conform as closely as possible to the [Google Style Guide]
(https://google.github.io/styleguide/pyguide.html). A pylint file is included
in this project's root directory, taken from that style guide. If you make
changes to the codebase and want to run pylint against them, you can do so
by running (from the root directory, with an appropriate environment activated):

`pylint <name of thing to lint>`

For instance, to run pylint against the full SchemaGenerator module itself, run:

`pylint schemagen`

Or, to run against the `main.py` script:

`pylint main.py`

