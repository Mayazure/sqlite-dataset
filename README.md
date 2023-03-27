# SQLite Dataset

Use [SQLite](https://sqlite.org/index.html) database to store datasets.
 
Based on [SQLAlchemy core](https://docs.sqlalchemy.org/en/20/core/).

## Usage

### Create a dataset

```python
from sqlite_dataset import SQLiteDataset
from sqlalchemy import Column, String, Integer

ds = SQLiteDataset.create(
    'test.db', 
    {'my_table': [
        Column('name', String),
        Column('age', Integer)
    ]}
)
```

### Connect to dataset
```python
ds = SQLiteDataset('test.db')
ds.add_many('my_table', [{'name': 'user2', 'age': 25}])
ds.close()
```

### Connect to dataset using context manager
```python
with SQLiteDataset('test.db') as ds:
    ds.add_many('my_table', [{'name': 'user3', 'age': 25}])
```

### Use with pandas
```python
import pandas as pd

with SQLiteDataset('test.db') as ds:
    df = pd.read_sql(
        ds.get_table('my_table').select(),
        ds.connection
    )
    
#     name  age
# 0  user1   25
# 1  user2   26
# 2  user3   27
```