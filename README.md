# SQLite Dataset

Use [SQLite](https://sqlite.org/index.html) database to store datasets. Based on [SQLAlchemy core](https://docs.sqlalchemy.org/en/20/core/).

## Structure

The core of sqlite-dataset is the Class **SQLiteDataset**, which wraps a SQLAlchemy connection to a SQLite database.

## Usage

### Create a new dataset

A **schema** is required to create a new dataset. The **schema** should be a dictionary where each item is a column.

There are two ways to specify the schema:

1. Extend the base **SQLiteDataset** class and override the **schema** field.

```python
from sqlite_dataset import SQLiteDataset
from sqlalchemy import Column, String, Float

class MyIrisDataset(SQLiteDataset):
    schema = {
        'iris': [
            Column('sepal_length_cm', String),
            Column('sepal_width_cm', Float),
            Column('petal_length_cm', Float),
            Column('petal_width_cm', Float),
            Column('class', String),
        ]
    }

ds = MyIrisDataset.create('test.db')
```

2. Pass schema to `SQLiteDataset.create()`

```python
schema = {
    'iris': [
        Column('sepal_length_cm', String),
        Column('sepal_width_cm', Float),
        Column('petal_length_cm', Float),
        Column('petal_width_cm', Float),
        Column('class', String),
    ]
}
ds = SQLiteDataset.create('test.db', schema=schema)
```

Be aware that the schema passed to `SQLiteDataset.create()` will override the class field schema.

### Connect to an existing dataset

An existing dataset could be one created by calling `SQLiteDataset.create()` as shown above, or could be any SQLite database file.

To connect to a dataset, call the `connect()` method and `close()` after complete all tasks.

```python
ds = SQLiteDataset('test.db')
ds.connect()
# do something
ds.close()
```

Or the dataset can be used as a context manager

```python
with SQLiteDataset('test.db') as ds:
    # do something
    pass
```

### Schema for existing dataset

**SQLiteDataset** object uses SQLAlchemy connection under the hood, soa schema is required to make any database queries or operations.

The way to specify schema for an existing dataset is similar to *create a new dataset*.

If it's a class extending the base SQLiteDataset class, and overrides the schema field, then this schema will be used.

```python
with MyIrisDataset('test.db') as ds:
    pass
```

Or a schema can be passed into the class constructor. The schema passed into the constructor will always override the class field schema.

```python
with MyIrisDataset('test.db', schema=schema) as ds:
    pass

with SQLiteDataset('test.db', schema=schema) as ds:
    pass
```

If no schema provided by either of the above, a [SQLAlchemy **reflection**](https://docs.sqlalchemy.org/en/13/core/reflection.html) is performed to load and parse schema from the existing database.

```python
with SQLiteDataset('test.db') as ds:
    pass
```

It is recommended to explicitly define the schema as **reflection** may have performance issue in some cases if the schema is very large and complex.

## Add and read data

```python
data = [
    {
        'sepal_length_cm': '5.1',
        'sepal_width_cm': '3.5',
        'petal_length_cm': '1.4',
        'petal_width_cm': '0.2',
        'class': 'setosa'
    },
    {
        'sepal_length_cm': '4.9',
        'sepal_width_cm': '3.0',
        'petal_length_cm': '1.4',
        'petal_width_cm': '0.2',
        'class': 'setosa'
    }
]

with MyIrisDataset('test.db') as ds:
    ds.insert_data('iris', data)
```

```python
with MyIrisDataset('test.db') as ds:
    res = ds.read_data('iris')
```


### Use with pandas

A pandas DataFrame can be inserted into a dataset by utilizing the `to_sql()` function, and read from the dataset using `read_sql` function.

Be aware that in this case, `SQLiteDataset()` should be used without specifying the schema.

```python
import seaborn as sns
import pandas as pd

df = sns.load_dataset('iris')
with SQLiteDataset('iris11.db') as ds:
    df.to_sql('iris', ds.connection)
    ds.connection.commit()
```

```python
with SQLiteDataset('iris11.db') as ds:
    res = pd.read_sql(
        ds.get_table('iris').select(),
        ds.connection
    )
```