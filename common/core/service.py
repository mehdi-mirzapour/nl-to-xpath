from typing import List, Tuple, Any, Type
from abc import ABC, abstractmethod
from fastapi.exceptions import HTTPException
from time import perf_counter
from common.database.repositories.requests import RequestRepository
from common.utils.logger import logger
from common.controller import GenericController
from .model import CoreModel
from .schema import (
    RequestSchema,
    ResponseSchema,
    TokenUsage,
)
from fastapi import Body


class CoreService(ABC, GenericController):
    request_model: Type[RequestSchema] = RequestSchema
    def __init__(self,app, url_prefix: str, client: Type[CoreModel]):
        super().__init__(app=app)
        self.client = client
        self.request_repo = RequestRepository()
        self.url_prefix = url_prefix
        self.add_api_route(self.url_prefix, self.main, methods=["POST"])
        self.app.include_router(self.router)

    @abstractmethod
    async def flow(
        self, *args, **kwargs
    ) -> Tuple[Any, List[TokenUsage]] | Tuple[HTTPException, None]:
        pass
    async def main(self, request: Any = Body(...)) -> ResponseSchema:
        # Force Pydantic to validate against the subclass's model
        parsed_request = self.request_model.model_validate(request)
        return await self._main(parsed_request)

    async def _main(self, request: Any = Body(...)) -> ResponseSchema:
        
        start = perf_counter()
        request_id = None

        try:
            request_id = await self.request_repo.add_request(
                endpoint_call=self.url_prefix, request_data=request.model_dump()
            )
        except Exception as e:
            logger.error(f"Unable to save request, error {e}")

        try:
            response = await self.flow(request)
            if isinstance(response, HTTPException):
                logger.error(f"flow Issue: {response.detail}")
                if request_id:
                    await self.request_repo.add_response(
                        request_id=request_id,
                        status=500,
                        response_data={},
                        error_message=response.detail,
                    )
                duration = perf_counter() - start
                return ResponseSchema(
                    status=500,
                    message="Error",
                    data=response.detail,
                    duration=duration,
                )
            if isinstance(response, tuple):
                response, openai_usage_tokens = response
            
                duration = perf_counter() - start
                model_response = ResponseSchema(
                    status=200,
                    message="Success",
                    data=response,
                    duration=duration,
                )
                try:
                    if isinstance(openai_usage_tokens, list):
                        tokens = [usage.model_dump() for usage in openai_usage_tokens]
                    else:
                        tokens = [openai_usage_tokens.model_dump()]
                    await self.request_repo.bulk_insert_token_usage(token_usages=tokens, request_id= request_id)
                except Exception as e:
                    logger.error(
                        f"Unable to store the tokens usage for request ID: {request_id}"
                    )
                return model_response
        except Exception as ex:
            logger.error(f"Unable to execute the flow issue : {ex}")
            duration = perf_counter() - start
            import traceback

            traceback.print_exc()
            return ResponseSchema(
                status=500,
                message="Error",
                data=ex,
                duration=duration,
            )
