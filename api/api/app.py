# from __future__ import annotations

# from litestar import Litestar, get, post, put
# from . import models
# from .config import db_config, provide_transaction, SQLAlchemyPlugin
# from litestar.controller import Controller

# from datetime import date
# from typing import TYPE_CHECKING
# from uuid import UUID

# from pydantic import BaseModel as _BaseModel
# from pydantic import TypeAdapter
# from sqlalchemy import ForeignKey, select
# from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

# from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
# from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin
# from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
# from litestar.controller import Controller
# from litestar.di import Provide
# from litestar.handlers.http_handlers.decorators import delete, patch, post
# from litestar.pagination import OffsetPagination
# from litestar.params import Parameter
# from litestar.repository.filters import LimitOffset


# @post()
# async def post_stations()

# class StationController(Controller):
#     """Station CRUD"""

#     dependencies = {"authors_repo": Provide(models.provide_station_repo)}

#     @get(path="/authors")
#     async def list_authors(
#         self,
#         stations_repo: models.StationRepository,
#     ) -> models.Station:
#         """List authors."""
#         results, total = await stations_repo.list_and_count()
#         type_adapter = TypeAdapter(list[Author])
#         return OffsetPagination[Author](
#             items=type_adapter.validate_python(results),
#             total=total,
#             limit=limit_offset.limit,
#             offset=limit_offset.offset,
#         )

#     @post(path="/authors")
#     async def create_author(
#         self,
#         authors_repo: AuthorRepository,
#         data: AuthorCreate,
#     ) -> Author:
#         """Create a new author."""
#         obj = await authors_repo.add(
#             AuthorModel(**data.model_dump(exclude_unset=True, exclude_none=True)),
#         )
#         await authors_repo.session.commit()
#         return Author.model_validate(obj)

#     # we override the authors_repo to use the version that joins the Books in
#     @get(path="/authors/{author_id:uuid}", dependencies={"authors_repo": Provide(provide_author_details_repo)})
#     async def get_author(
#         self,
#         authors_repo: AuthorRepository,
#         author_id: UUID = Parameter(
#             title="Author ID",
#             description="The author to retrieve.",
#         ),
#     ) -> Author:
#         """Get an existing author."""
#         obj = await authors_repo.get(author_id)
#         return Author.model_validate(obj)

#     @patch(
#         path="/authors/{author_id:uuid}",
#         dependencies={"authors_repo": Provide(provide_author_details_repo)},
#     )
#     async def update_author(
#         self,
#         authors_repo: AuthorRepository,
#         data: AuthorUpdate,
#         author_id: UUID = Parameter(
#             title="Author ID",
#             description="The author to update.",
#         ),
#     ) -> Author:
#         """Update an author."""
#         raw_obj = data.model_dump(exclude_unset=True, exclude_none=True)
#         raw_obj.update({"id": author_id})
#         obj = await authors_repo.update(AuthorModel(**raw_obj))
#         await authors_repo.session.commit()
#         return Author.from_orm(obj)

#     @delete(path="/authors/{author_id:uuid}")
#     async def delete_author(
#         self,
#         authors_repo: AuthorRepository,
#         author_id: UUID = Parameter(
#             title="Author ID",
#             description="The author to delete.",
#         ),
#     ) -> None:
#         """Delete a author from the system."""
#         _ = await authors_repo.delete(author_id)
#         await authors_repo.session.commit()
# app = Litestar(
#     dependencies={"transaction": provide_transaction},
#     plugins=SQLAlchemyPlugin(db_config),
# )

# # app = Litestar([get_list, add_item, update_item], lifespan=[db_connection])
