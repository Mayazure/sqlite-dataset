import pandas as pd
from sqlalchemy import Column, String, Float
#
from sqlite_dataset import SQLiteDataset
#
#
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
#
# # ds = MyIrisDataset.create('iris.db')
#
# data = [
#     {
#         'sepal_length_cm': '5.1',
#         'sepal_width_cm': '3.5',
#         'petal_length_cm': '1.4',
#         'petal_width_cm': '0.2',
#         'class': 'setosa'
#     },
#     {
#         'sepal_length_cm': '4.9',
#         'sepal_width_cm': '3.0',
#         'petal_length_cm': '1.4',
#         'petal_width_cm': '0.2',
#         'class': 'setosa'
#     }
# ]
#
# with MyIrisDataset('iris.db') as ds:
#     # ds.insert_data('iris', data)
#     res = ds.read_data('iris')
#     print(res)

import seaborn as sns

df = sns.load_dataset('iris')
with SQLiteDataset('iris11.db') as ds:
    # df.to_sql('iris', ds.connection)
    # ds.connection.commit()
    res = pd.read_sql(
        ds.get_table('iris').select(),
        ds.connection
    )
    print(res)
