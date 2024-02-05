from __future__ import annotations

from typing import Protocol, Any, List, Dict
from uuid import UUID

from library.core.entities import Entity


class Repository(Protocol):

    def create(
        self, input_entity: Entity, table_name: str
    ) -> None:
        pass

    def read_one(
        self, entity_id: UUID, table_name: str, column_name: str
    ) -> Dict[str, object]:
        pass

    def read_multi(
        self, entity_id: UUID, table_name: str, column_name: str = "USER_KEY"
    ) -> List[Dict[str, object]]:
        pass

    def update(self, entity_id: UUID, column_name: str, table_name: str, changes: Dict[str, Any]) -> None:
        pass
