from fastapi import FastAPI, APIRouter
from typing import Callable, List, Optional, Any


class RouteBuilder:
    """
    A helper class to modularly build and register API routes
    using FastAPI's APIRouter.

    Attributes:
        app (FastAPI): The main FastAPI application instance.
        router (APIRouter): A dedicated router for grouping related endpoints.
    """

    def __init__(self, app: FastAPI) -> None:
        """
        Initialize the RouteBuilder with a FastAPI app instance.

        Args:
            app (FastAPI): The FastAPI app to attach routes to.
        """
        self.app: FastAPI = app
        self.router: APIRouter = APIRouter()

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: List[str],
        dependencies: Optional[List[Any]] = None,
    ) -> None:
        """
        Add a new API route to the internal router.

        Args:
            path (str): The URL path of the route (e.g., "/predict").
            endpoint (Callable): The function to handle requests.
            methods (List[str]): HTTP methods accepted (e.g., ["GET", "POST"]).
            dependencies (Optional[List[Any]]): FastAPI dependencies to apply (default: empty list).
        """
        self.router.add_api_route(
            path=path,
            endpoint=endpoint,
            methods=methods,
            dependencies=dependencies or [],
        )

    def register_routes(self) -> None:
        """
        Include the internal router in the main FastAPI app.

        Call this after adding all desired routes.
        """
        self.app.include_router(self.router)
