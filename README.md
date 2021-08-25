

Input File Assumptions:

- must be a CSV
- first row must be a header row (todo: allow providing a secondary (JSON?) file that has the column names)
- all rows must contain a value (could be null or blank) for all columns
- lots of options for how to do this; could use pandas to read into a dataframe

To import as a module

```
import schemaGen
schema_generator = schemaGen.SchemaGenerator()
```

To run as a program
from the main project directory
`python main.py <inputfile>`

To run tests:

Run all tests from the main project directory:
`python -m unittest`
Run a single test, from the main project directory:
`python -m unittest -k test__build_schema`
