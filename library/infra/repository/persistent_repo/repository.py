import sqlite3
from typing import Any, Dict, List, Tuple
from uuid import UUID

from constants import DB_NAME
from library.core.entities import IEntity
from library.core.errors import DoesNotExistError, DoesNotExistErrorTable
from library.core.serialization import Serializer


class PersistentRepository:
    def __init__(self) -> None:
        path = DB_NAME + ".db"
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.con.row_factory = self.dict_factory
        self.cur = self.con.cursor()
        self.tables = {
            "users": ["key"],
            "wallets": ["address", "bitcoins", "user_key", "key"],
            "transactions": [
                "address_from",
                "address_to",
                "amount",
                "fee_amount",
                "key",
            ],
        }

        for table in self.tables.keys():
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS "
                + table
                + "("
                + ", ".join(self.tables[table])
                + ")"
            )

    @staticmethod
    def dict_factory(
        cursor: sqlite3.Cursor, row: Tuple[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create(self, input_entity: IEntity, table_name: str) -> None:
        execute_str = (
            "INSERT INTO {} VALUES(".format(table_name)
            + ", ".join([":" + i for i in self.tables[table_name]])
            + ");"
        )
        inputs = Serializer().serialize(input_entity, self.tables[table_name])
        self.cur.execute(execute_str, inputs)
        self.con.commit()

    def read_one(
        self, entity_id: UUID, table_name: str, column_name: str
    ) -> Dict[str, object]:
        try:
            str_to_execute = "SELECT * FROM {} WHERE {}='{}'".format(
                table_name, column_name, entity_id
            )
            fetch: Dict[str, object] = self.cur.execute(str_to_execute).fetchone()
            if len(fetch) == 0:
                raise DoesNotExistError(table_name, column_name, str(entity_id))
            return fetch
        except KeyError:
            raise DoesNotExistError(table_name, column_name, str(entity_id))
        except TypeError:
            raise DoesNotExistError(table_name, column_name, str(entity_id))

    def read_multi(
        self, entity_id: UUID, table_name: str, column_name: str = "USER_KEY"
    ) -> List[Dict[str, object]]:
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
            raise DoesNotExistError(table_name, column_name, str(entity_id))
        except TypeError:
            raise DoesNotExistError(table_name, column_name, str(entity_id))

    def read_all(self, table_name: str) -> List[Dict[str, object]]:
        try:
            str_to_execute = f"SELECT * FROM {table_name}"
            cursor = self.cur.execute(str_to_execute)
            result = []
            for row in cursor:
                result.append(row)
            return result
        except KeyError:
            raise DoesNotExistErrorTable(table_name)
        except TypeError:
            raise DoesNotExistErrorTable(table_name)

    def update(
        self,
        entity_id: UUID,
        column_name: str,
        table_name: str,
        changes: Dict[str, Any],
    ) -> None:
        try:
            self.read_one(entity_id, table_name, column_name)
            set_sql = ", ".join(
                [
                    "{}={}".format(
                        k,
                        (
                            '"' + str(changes[k]) + '"'
                            if isinstance(changes[k], str)
                            else changes[k]
                        ),
                    )
                    for k in changes.keys()
                ]
            )
            sql_query = "UPDATE {} SET {} WHERE {} = '{}'".format(
                table_name, set_sql, column_name, entity_id
            )
            self.cur.execute(sql_query)
            self.con.commit()
        except KeyError:
            raise DoesNotExistError(table_name, column_name, str(entity_id))

    def drop_all(self) -> None:
        for table in self.tables.keys():
            self.cur.execute("DROP TABLE " + table)
