"""Regression tests for the authshield-lab relative-import repair.

Before this repair, 105 sites across `app/collaboration` and `app/ecosystem`
used absolute imports of packages that do not exist -- e.g.

    from domain.entities.research_workspace import ResearchProject

`domain` is not a top-level package (the real path is
`app.collaboration.domain...`), so the statement raised
`ModuleNotFoundError: No module named 'domain'` the moment the function ran.
Nothing noticed, because every feature-router import in
`app/api/v1/router.py` is wrapped in
`try: ... except (ImportError, AttributeError): pass`, so those areas were
silently never registered.

Three distinct defects are covered here:

1. the unresolvable absolute imports (105 sites, 20 files),
2. `domain.interfaces` imported only under `if TYPE_CHECKING:` while being
   used as a *runtime* base class, so the module raised
   `NameError: name 'AcademicHubRepository' is not defined` on import,
3. string literals assigned to `(str, Enum)`-typed entity fields, which
   silently stored a bare `str` where later code reads `.value`.
"""

from __future__ import annotations

import importlib
import pathlib
import typing

import pytest

import app

# Scoped to the two areas this repair covered. `pkgutil.walk_packages` is not
# used: it imports while discovering, which trips an unrelated pre-existing
# SQLAlchemy declarative-mapper problem in `app.services.database`.
_AREAS = ("collaboration", "ecosystem")
_EXTRA = ("app.lms.domain.models.lms_models",)
_APP_ROOT = pathlib.Path(app.__file__).parent


def _module_names_under(rel_dir: str) -> list[str]:
    base = _APP_ROOT / rel_dir
    out = []
    for path in sorted(base.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        mod = "app." + str(path.relative_to(_APP_ROOT).with_suffix("")).replace("/", ".")
        out.append(mod)
    return out


ALL_MODULES = sorted(_module_names_under(_AREAS[0]) + _module_names_under(_AREAS[1]) + list(_EXTRA))


def test_sweep_actually_enumerated_the_areas() -> None:
    """Guard the guard: a discovery bug would make the sweep below vacuous."""
    assert len(ALL_MODULES) > 30
    for expected in (
        "app.collaboration.services.research_service",
        "app.collaboration.repositories.collaboration_repository_impl",
        "app.ecosystem.services.marketplace_service",
        "app.lms.domain.models.lms_models",
    ):
        assert expected in ALL_MODULES


@pytest.mark.parametrize("module_name", ALL_MODULES)
def test_every_app_module_imports(module_name: str) -> None:
    """No app module may raise on import.

    Catches the whole 105-site class at once. A NameError here is defect (2)
    above; a ModuleNotFoundError is defect (1) or a too-shallow relative
    import such as `from ...shared...` resolving to `app.lms.shared`.
    """
    importlib.import_module(module_name)


def test_research_service_create_project_actually_runs() -> None:
    """The exact call that raised `No module named 'domain'` before.

    Driven against the real in-memory repository, not a MagicMock -- a mock
    fabricates any attribute, which is how these defects stayed invisible.
    """
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryResearchWorkspaceRepository,
    )
    from app.collaboration.services.research_service import ResearchService

    repo = InMemoryResearchWorkspaceRepository()
    project = ResearchService(repo).create_project(
        name="P",
        description="D",
        principal_investigator="pi",
    )
    assert project.name == "P"
    assert repo.get_project(project.id) is not None


def test_in_memory_repositories_really_subclass_their_interfaces() -> None:
    """Defect (2): interfaces used as runtime bases behind TYPE_CHECKING."""
    from app.collaboration.domain.interfaces import (
        AcademicHubRepository,
        KnowledgeBaseRepository,
        PeerReviewRepository,
        ResearchWorkspaceRepository,
    )
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryAcademicHubRepository,
        InMemoryKnowledgeBaseRepository,
        InMemoryPeerReviewRepository,
        InMemoryResearchWorkspaceRepository,
    )

    for impl, abc in (
        (InMemoryAcademicHubRepository, AcademicHubRepository),
        (InMemoryResearchWorkspaceRepository, ResearchWorkspaceRepository),
        (InMemoryPeerReviewRepository, PeerReviewRepository),
        (InMemoryKnowledgeBaseRepository, KnowledgeBaseRepository),
    ):
        assert issubclass(impl, abc), f"{impl.__name__} is not a real {abc.__name__}"


def test_update_knowledge_map_is_on_the_interface() -> None:
    """The service called a method the ABC never declared."""
    from app.collaboration.domain.interfaces import ResearchWorkspaceRepository

    assert hasattr(ResearchWorkspaceRepository, "update_knowledge_map")


def test_status_fields_hold_real_enum_members_not_bare_strings() -> None:
    """Defect (3): `"published"` stored where `ArticleStatus` is declared.

    A bare `str` compares equal to the member, so the old code looked fine --
    but `.value` raises AttributeError on it, and
    `ecosystem_repository_impl.search_items` does read `.value`.
    """
    from app.collaboration.domain.entities.knowledge_base import ArticleStatus
    from app.collaboration.repositories.collaboration_repository_impl import (
        InMemoryKnowledgeBaseRepository,
    )
    from app.collaboration.services.knowledge_base_service import (
        KnowledgeBaseService,
    )

    repo = InMemoryKnowledgeBaseRepository()
    service = KnowledgeBaseService(repo)
    article = service.create_article(title="t", content="c", category="c", author="a")

    published = service.publish_article(article.id)
    assert published.status is ArticleStatus.published
    assert published.status.value == "published"

    archived = service.archive_article(article.id)
    assert archived.status is ArticleStatus.archived
    assert archived.status.value == "archived"


def test_marketplace_installation_record_holds_real_enum() -> None:
    from app.ecosystem.domain.entities.marketplace import InstallStatus, LocalPackage
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryMarketplaceRepository,
    )
    from app.ecosystem.services.marketplace_service import MarketplaceService

    repo = InMemoryMarketplaceRepository()
    pkg = LocalPackage(name="p", version="1.0", author="a", description="d", category="c")
    repo.add_package(pkg)

    record = MarketplaceService(repo).install_package(pkg.id, "user-1")
    assert record.status is InstallStatus.installed
    assert record.status.value == "installed"


def test_organisation_type_stays_free_form_and_never_raises() -> None:
    """`Organization.org_type` is declared `OrgType` but assigned a raw `str`.

    Nothing ever reads ``org_type.value`` -- the only ``.value`` read in the
    ecosystem repository is ``LibraryItem.item_type.value`` -- so the value is
    genuinely free-form and the API accepts any string. Coercing it with
    ``OrgType(org_type)`` would turn an unvalidated value into an unhandled
    ``ValueError`` (HTTP 500) for any caller passing e.g. ``"school"``.

    This test pins the *safe* behaviour so the type mismatch cannot later be
    "fixed" by adding an unguarded coercion.
    """
    from app.ecosystem.domain.entities.institution import OrgType
    from app.ecosystem.repositories.ecosystem_repository_impl import (
        InMemoryInstitutionRepository,
    )
    from app.ecosystem.services.institution_service import InstitutionService

    repo = InMemoryInstitutionRepository()

    known = InstitutionService(repo).create_organization("Acme", "university")
    assert known.org_type == "university"
    assert OrgType(known.org_type) is OrgType.university

    # A value outside the enum must still be accepted rather than raising.
    free_form = InstitutionService(repo).create_organization("Other", "school")
    assert free_form.org_type == "school"


def test_collaboration_and_ecosystem_areas_are_registered() -> None:
    """The point of the whole repair: these areas now exist on the app."""
    from fastapi.routing import APIRoute

    from app.api.v1.router import api_v1_router

    mounted = {r.path for r in api_v1_router.routes if isinstance(r, APIRoute)}
    assert any(p.startswith("/api/v1/collaboration") for p in mounted), sorted(mounted)[:10]
    assert any(p.startswith("/api/v1/ecosystem") for p in mounted)
    assert not any("/api/v1/api/v1/" in p for p in mounted)


def test_event_handler_dispatch_tables_are_typed_for_callers() -> None:
    """`handler = _HANDLERS.get(type(event))` then calling it needs a type."""
    from app.collaboration.events import collaboration_event_handlers as collab
    from app.ecosystem.events import ecosystem_event_handlers as eco

    assert isinstance(collab._HANDLERS, typing.Mapping)
    assert callable(eco.dispatch)
