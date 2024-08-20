from src.repositories import RoleRepository


class RoleHelper:
    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repository = role_repository

    async def insert_role(self, book: dict):
        return await self.role_repository.insert_book(book)

    async def get_role(self, name: str):
        return await self.role_repository.get_by_name(name)
