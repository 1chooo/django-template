from types import ModuleType
from uuid import UUID

from django.core.handlers.wsgi import WSGIRequest
from django.db.utils import IntegrityError
from ninja_extra import ControllerBase, api_controller, route

from common.exceptions import Http400BadRequestException, Http403ForbiddenException, Http404NotFoundException
from common.models import BaseModel
from common.schemas import BaseResponseSchema, Http401UnauthorizedSchema, Http404NotFoundSchema


def generate_crud_controller(  # noqa: C901
    model: type[BaseModel],
    model_name: str,
    controller_prefix: str,
    application_schemas: ModuleType,
) -> type[ControllerBase]:
    """Generate a CRUD controller for a model.

    Args:
        model (type[BaseModel]): The model for which to generate the CRUD controller.
        model_name (str): The name of the model.
        controller_prefix (str): The prefix for the controller.
        application_schemas (ModuleType): The module containing the application schemas.
    """

    @api_controller(
        prefix_or_class=controller_prefix,
        tags=[f"edit {model_name}"],
    )
    class CRUDController:
        Model = model

        @route.post(
            "",
            response={
                200: getattr(application_schemas, f"Get{model_name}ResponseSchema"),
                401: Http401UnauthorizedSchema,
            },
        )
        def create(
            self,
            request: WSGIRequest,
            body: getattr(application_schemas, f"Create{model_name}Schema"),  # type: ignore
        ) -> BaseModel:
            q = self.Model(**body.dict())

            try:
                q.save(request.user)
            except IntegrityError as e:
                raise Http400BadRequestException("code already exists") from e

            return q

        @route.get(
            "",
            response={
                200: list[getattr(application_schemas, f"Get{model_name}ResponseSchema")],
                401: Http401UnauthorizedSchema,
            },
        )
        def get_all(
            self,
            request: WSGIRequest,
        ) -> list[BaseModel]:
            return self.Model.objects.filter(created_by_user=request.user).values()  # type: ignore

        @route.get(
            "/{pk}",
            response={
                200: getattr(application_schemas, f"Get{model_name}ResponseSchema"),
                401: Http401UnauthorizedSchema,
                404: Http404NotFoundSchema,
            },
        )
        def get(self, request: WSGIRequest, pk: UUID) -> BaseModel:
            try:
                q = self.Model.objects.get(id=pk)
            except self.Model.DoesNotExist as e:
                raise Http404NotFoundException from e

            if q.company_id != request.user.company_id:  # type: ignore
                raise Http403ForbiddenException("You don't have permission to get this object.")

            return q

        @route.put(
            "/{pk}",
            response={
                200: BaseResponseSchema,
                401: Http401UnauthorizedSchema,
                404: Http404NotFoundSchema,
            },
        )
        def update(
            self,
            request: WSGIRequest,
            pk: UUID,
            body: getattr(application_schemas, f"Put{model_name}Schema"),  # type: ignore
        ) -> dict:
            try:
                q = self.Model.objects.get(id=pk)
            except self.Model.DoesNotExist as e:
                raise Http404NotFoundException from e

            if q.company_id != request.user.company_id:  # type: ignore
                raise Http403ForbiddenException("You don't have permission to update this object.")

            for k, v in body.dict().items():
                setattr(q, k, v)

            try:
                q.save(request.user)
            except IntegrityError as e:
                raise Http400BadRequestException("code already exists") from e

            return {"msg": "success"}

        @route.delete(
            "/{pk}",
            response={
                200: BaseResponseSchema,
                401: Http401UnauthorizedSchema,
                404: Http404NotFoundSchema,
            },
        )
        def delete(self, request: WSGIRequest, pk: UUID) -> dict:
            try:
                q = self.Model.objects.get(id=pk)
            except self.Model.DoesNotExist as e:
                raise Http404NotFoundException from e

            if q.company_id != request.user.company_id:  # type: ignore
                raise Http403ForbiddenException("You don't have permission to delete this object.")

            q.delete(request.user)

            return {"msg": "success"}

    return CRUDController
