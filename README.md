# SQLite Dataset

Use [SQLite](https://sqlite.org/index.html) database to store datasets. Based on [SQLAlchemy core](https://docs.sqlalchemy.org/en/20/core/).

## Structure

The core of sqlite-dataset is the Class **SQLiteDataset**, which wraps a SQLAlchemy connection to a SQLite database.

## Usage

### Declare a dataset

To declare a dataset, extend the base **SQLiteDataset** class and specify fields.

```python
from sqlite_dataset import SQLiteDataset, Field, String, Float

class MyIrisDataset(SQLiteDataset):
    
    sepal_length_cm = Field(String, tablename='iris')
    sepal_width_cm = Field(Float, tablename='iris')
    petal_length_cm = Field(Float, tablename='iris')
    petal_width_cm = Field(Float, tablename='iris')
    class_field = Field(String, tablename='iris', name='class')

ds = MyIrisDataset('my_iris_dataset.db')
```

This will create a sqlite database file on the specified path. If a dataset already exists, it will then be loaded. 

#### The *Field* object

`Field` can be seen as a factory that can create a SQLAlchemy's Column object.

The `Field` object's constructor takes same arguments as `sqlalchemy.schema.Column` with the difference that `Field` does not take positional name argument and has an extra keyword argument `tablename`.

Declare a Column using sqlalchemy.Column:

```python
from sqlalchemy import Column, String

Column('sepal_length_cm', String)
Column(name='sepal_length_cm', type_=String)
```

Declare a sqlite_dataset.Field:

```python
from sqlite_dataset import Field, String

sepal_length_cm = Field(String)
```

The variable name will be automatically used as the column name.

Column name can also be specified using `name` argument, which is useful if the column name is a Python preserved keyword:

```python
from sqlite_dataset import SQLiteDataset, Field, String

class MyDataset(SQLiteDataset):
    class_field = Field(String, name='class')
    type_field = Field(String, name='type')
```

Table name can be specified using `tablename` keyword argument:

```python
from sqlite_dataset import SQLiteDataset, Field, String

class MyDataset(SQLiteDataset):
    class_field = Field(String, name='class', tablename='table1')
    type_field = Field(String, name='type', tablename='table2')
```

This will create two tables: table1, table2.

If tablename is not specified, the column will be created in default table **data**. 

#### Field type and keyword arguments

The field type is the sqlalchemy column type. All sqlalchemy members were imported into sqlite_dataset.

```python
from sqlalchemy import String, Integer
```

is exactly the same as:

```python
from sqlite_dataset import String, Integer
```

### Inheritance

Dataset can be inherited.

```python
from sqlite_dataset import SQLiteDataset, Field, String, Float

class BaseDataset(SQLiteDataset):
    class_field = Field(String, tablename='iris', name='class')
    example_field = Field(String, tablename='example_table')

class ChildDataset(BaseDataset): 
    sepal_length_cm = Field(String, tablename='iris')
    sepal_width_cm = Field(Float, tablename='iris')
    petal_length_cm = Field(Float, tablename='iris')
    petal_width_cm = Field(Float, tablename='iris')
```

### Connect to an existing dataset

To connect to a dataset, call the `connect()` method. Call `close()` to close it.

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

**SQLiteDataset** object uses SQLAlchemy connection under the hood, so a schema is required to make any database queries or operations.

If no schema provided by either of the above, a [SQLAlchemy **reflection**](https://docs.sqlalchemy.org/en/13/core/reflection.html) is performed to load and parse schema from the existing database.

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