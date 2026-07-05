from abc import ABC, abstractmethod
import logging

from app.ai.router.enums import DataSource
from app.ai.router.schemas import RouteDecision
from app.ai.retrieval.schemas import RetrievalResult

logger = logging.getLogger(__name__)


class BaseRetriever(ABC):

    @property
    @abstractmethod
    def source(self) -> DataSource:
        """
        Returns the data source handled by this retriever.
        """
        raise NotImplementedError

    @abstractmethod
    async def retrieve(
        self,
        route: RouteDecision
    ) -> RetrievalResult:
        """
        Retrieve information for the supplied route.
        """
        raise NotImplementedError

    def supports(
        self,
        route: RouteDecision
    ) -> bool:
        """
        Check whether this retriever should handle the route.
        """
        return self.source in route.required_sources

    def validate(
        self,
        route: RouteDecision
    ) -> bool:
        """
        Validate the incoming route.
        Override in subclasses if needed.
        """
        return True