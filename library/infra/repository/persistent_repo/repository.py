import sqlite3
from typing import Any
from uuid import UUID

from constants import DB_NAME
from library.core.entities import Entity
from library.core.errors import (
    ClosedError,
    DoesNotExistError,
    DuplicateError,
    UndefinedTableException,
)
from library.core.serialization import SerializerForDB

"""
def deserialize_row(
    table_name: str, row: dict[str, object]
) -> Unit | Product | Receipt | Purchase:
    if table_name == "units":
        return SerializerForDB().deserialize_unit(row)
    elif table_name == "products":
        return SerializerForDB().deserialize_product(row)
    elif table_name == "receipts":
        return SerializerForDB().deserialize_receipt(row)
    elif table_name == "purchases":
        return SerializerForDB().deserialize_purchase(row)
    else:
        raise UndefinedTableException
"""


class PersistentRepository:
    def __init__(self) -> None:
        path = DB_NAME + ".db"
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = self.dict_factory
        self.cur = self.con.cursor()
        self.tables = {
            "users": ["key"],
            "wallets": ["address", "bitcoins", "user_key"]
        }

        for table in self.tables.keys():
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS "
                + table
                + "("
                + ", ".join(self.tables[table])
                + ")"
            )

    # taken from:
    # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
    @staticmethod
    def dict_factory(
        cursor: sqlite3.Cursor, row: tuple[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create(
        self, input_entity: Entity, table_name: str
    ) -> None:
        execute_str = (
                "INSERT INTO {} VALUES(".format(table_name)
                + ", ".join([":" + i for i in self.tables[table_name]])
                + ");"
        )
        inputs = SerializerForDB().serialize(
            table_name, input_entity, self.tables[table_name]
        )
        self.cur.execute(execute_str, inputs)
        self.con.commit()

    def read_one(
        self, entity_id: UUID, table_name: str, column_name: str = "KEY"
    ) -> dict[str, object]:
        try:
            str_to_execute = "SELECT * FROM {} WHERE {}='{}'".format(
                table_name, column_name, entity_id
            )
            fetch: dict[str, object] = self.cur.execute(str_to_execute).fetchone()
            if len(fetch) == 0:
                raise DoesNotExistError(entity_id)
            return fetch
        except KeyError:
            raise DoesNotExistError(entity_id)
        except TypeError:
            raise DoesNotExistError(entity_id)

    def read_multi(
        self, entity_id: UUID, table_name: str, column_name: str = "USER_KEY"
    ) -> list[dict[str, object]]:
        try:
            str_to_execute = "SELECT * FROM {} WHERE {}='{}'".format(
                table_name, column_name, entity_id
            )
            cursor = self.cur.execute(str_to_execute)
            result = []
            for row in cursor:
                result.append(row)
            return result
        except KeyError:
            raise DoesNotExistError(entity_id)
        except TypeError:
            raise DoesNotExistError(entity_id)

    """
    def read_all(self, table_name: str) -> list[dict[str, object]]:
        cursor = self.cur.execute("SELECT * FROM {}".format(table_name))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def update(
        self, entity_id: UUID, table_name: str, changes: dict[str, object]
    ) -> None:
        try:
            self.read_one(entity_id, table_name)  # will throw exception if needed
            set_sql = ", ".join(
                [
                    "{}={}".format(
                        k,
                        '"' + str(changes[k]) + '"'
                        if isinstance(changes[k], str)
                        else changes[k],
                    )
                    for k in changes.keys()
                ]
            )
            sql_query = "UPDATE {} SET {} WHERE id = '{}'".format(
                table_name, set_sql, entity_id
            )
            self.cur.execute(sql_query)
            self.con.commit()
        except KeyError:
            raise DoesNotExistError(entity_id)

    def delete(self, entity_id: UUID, table_name: str) -> None:
        try:
            self.read_one(entity_id, table_name)
            str_to_execute = "SELECT * FROM {} WHERE ID='{}'".format(
                table_name, entity_id
            )
            result = self.cur.execute(str_to_execute).fetchone()

            if table_name == "receipts" and result["status"] == "closed":
                raise ClosedError(entity_id)
            else:
                str_to_execute = "DELETE FROM {} WHERE ID='{}'".format(
                    table_name, entity_id
                )
                self.cur.execute(str_to_execute)
                self.con.commit()
        except KeyError:
            raise DoesNotExistError(entity_id)
    """
    def drop_all(self) -> None:
        for table in self.tables.keys():
            self.cur.execute("DROP TABLE " + table)
            
