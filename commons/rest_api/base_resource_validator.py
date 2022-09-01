from typing import Type

from commons.logging import log_error

from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.http_exceptions import ConflictException, NotFoundException


class BaseResourceValidator:
    resource_dao_class = None

    def __init__(self, resource_dao_class: Type[BaseDao]):
        self.resource_dao_class = resource_dao_class
        self.resource_bl_model_class = resource_dao_class.resource_bl_model_class

    def raise_not_exists(self, filters: dict):
        where_message_parts = [f'{key}={str(value)}' for key, value in filters.items()]
        where_message = ' AND '.join(where_message_parts)

        message = f'Could not find resource {self.resource_bl_model_class.__name__} where: {where_message}.'
        log_error(message)
        raise NotFoundException(message)

    def raise_resource_id_does_not_match_model(self, resource_id: int, model: BaseBLModel):
        message = f'Resource {self.resource_bl_model_class.__name__} ID {resource_id} does not match provided model ID {model.id}'
        log_error(message)
        raise ConflictException(message)

    def raise_unique_constraint(self, field: str, value: str):
        message = f'Resource {self.resource_bl_model_class.__name__} with {field}={value} already exists.'
        log_error(message)
        raise ConflictException(message)

    def validate_resource_id_matches_model(self, resource_id, model: BaseBLModel):
        if resource_id != model.id:
            self.raise_resource_id_does_not_match_model(resource_id, model)

    def validate_resource_id_exists(self, resource_id: int):
        if not self.resource_dao_class.exists(resource_id):
            self.raise_not_exists({'id': resource_id})

    def validate_resource_is_unique_by_field(self, field: str, value: str):
        if self.resource_dao_class.exists_by_field(field, value):
            self.raise_unique_constraint(field, value)