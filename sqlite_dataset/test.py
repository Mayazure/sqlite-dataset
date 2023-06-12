import pandas as pd

from sqlite_dataset import SQLiteDataset, Field, String, Float
from sqlite_dataset.fields import DataTable


class MyBaseIrisDataset(SQLiteDataset):
    __defaulttable__ = 'sentence'

    text = Field(String)
    iris = DataTable(
        sepal_length_cm=Field(String, tablename='iris')
    )


class MyIrisDataset(MyBaseIrisDataset):
    iris = DataTable(
        sepal_width_cm=Field(Float),
        petal_length_cm=Field(Float),
        petal_width_cm=Field(Float),
        class_field=Field(String, name='class')
    )


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

with MyIrisDataset('iris.db') as ds:
    ds.insert_data('iris', data)
    # res = ds.read_data('iris')
    # print(res)

with MyIrisDataset('iris11.db') as ds:
    ds.insert_data('iris', data)

with MyIrisDataset('iris.db') as ds:
    res = ds.read_data('iris')
    print(res)

# import seaborn as sns

# df = sns.load_dataset('iris')
# with MyIrisDataset('iris11.db') as ds:
#     df.to_sql('iris', ds.connection)
#     ds.connection.commit()
#     # res = pd.read_sql(
#     #     ds.get_table('iris').select(),
#     #     ds.connection
#     # )
#     # print(res)
