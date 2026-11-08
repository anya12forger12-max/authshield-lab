"""Configurable security pipeline for authentication requests."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


@dataclass
class PipelineStage:
    """A single stage within the security pipeline."""

    name: str
    handler: Callable[..., Coroutine[Any, Any, Any]]
    order: int = 0


class SecurityPipeline:
    """Configurable security pipeline for authentication requests.

    Stages are sorted by ``order`` before execution and each stage receives
    the shared *context* dictionary.  A stage may modify the context in-place
    (e.g. to attach a verified identity) or raise an exception to short-
    circuit the pipeline.
    """

    def __init__(self) -> None:
        self._stages: list[PipelineStage] = []

    def add_stage(
        self,
        name: str,
        handler: Callable[..., Coroutine[Any, Any, Any]],
        order: int = 0,
    ) -> None:
        """Register a pipeline stage.

        Parameters
        ----------
        name:
            Human-readable stage identifier.  Duplicate names are rejected.
        handler:
            An async callable that receives the pipeline context dict.
        order:
            Numeric sort key; lower values run first.

        Raises
        ------
        ValueError
            If a stage with *name* is already registered.
        """
        if any(s.name == name for s in self._stages):
            raise ValueError(f"Stage '{name}' is already registered")
        self._stages.append(PipelineStage(name=name, handler=handler, order=order))

    def remove_stage(self, name: str) -> None:
        """Remove a stage by *name*.

        Raises
        ------
        KeyError
            If no stage with *name* exists.
        """
        for idx, stage in enumerate(self._stages):
            if stage.name == name:
                self._stages.pop(idx)
                return
        raise KeyError(f"Stage '{name}' not found")

    def get_stages(self) -> list[PipelineStage]:
        """Return the ordered list of registered stages."""
        return sorted(self._stages, key=lambda s: s.order)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run all stages in order, passing the shared *context*.

        Each stage handler receives the context dict and may augment it.  If
        any stage raises, the pipeline is aborted and the exception propagates
        to the caller.

        Returns
        -------
        dict[str, Any]
            The (potentially modified) context dictionary.
        """
        for stage in self.get_stages():
            logger.debug("Pipeline executing stage: %s", stage.name)
            await stage.handler(context)
        return context

    def clear(self) -> None:
        """Remove all registered stages."""
        self._stages.clear()
