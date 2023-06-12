from sqlalchemy import Column


class Field:

    def __init__(self, type_pos=None, *args, name=None, tablename=None, **kwargs):
        self.args = args
        self.type_pos = type_pos
        self.kwargs = kwargs
        self.name = name
        self.tablename=tablename

    def new_column(self, name=None):
        col_name = self.name if self.name else name
        return Column(col_name, self.type_pos, *self.args, **self.kwargs)


class DataTable:

    def __init__(self, _tablename=None, **kwargs):
        self.tablename=_tablename
        self.fields = []
        for name, field in kwargs.items():
            if isinstance(field, Field):
                self.fields.append((name, field))
