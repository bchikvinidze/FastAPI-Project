from __future__ import annotations

from typing import Protocol
from uuid import UUID

from library.core.entities import Entity


class Repository(Protocol):

    def create(
        self, input_entity: Entity, table_name: str
    ) -> None:
        pass

    def read_one(
        self, entity_id: UUID, table_name: str, column_name: str
    ) -> dict[str, object]:
        pass

    def read_multi(
        self, entity_id: UUID, table_name: str, column_name: str = "USER_KEY"
    ) -> list[dict[str, object]]:
        pass

    def update(self, entity_id: UUID, column_name: str, table_name: str, changes: dict[str, object]) -> None:
        pass
