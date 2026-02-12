from core.state_machine.states import ProjectState
from core.errors import GuardFailure


def guard_has_brand_memory(project) -> None:
    if project.brand_memory is None:
        raise GuardFailure(
            "has_brand_memory",
            "Project must have brand memory before planning",
        )


def guard_has_site_plan(project) -> None:
    if project.site_plan is None:
        raise GuardFailure(
            "has_site_plan",
            "Project must have a site plan before generation",
        )


def guard_has_site_version(project) -> None:
    if project.site_version is None:
        raise GuardFailure(
            "has_site_version",
            "Project must have a generated site before preview",
        )


# Guards keyed by the TARGET state they protect
TRANSITION_GUARDS: dict[ProjectState, list] = {
    ProjectState.PLAN_READY: [guard_has_brand_memory],
    ProjectState.SITE_GENERATED: [guard_has_site_plan],
    ProjectState.PREVIEW: [guard_has_site_version],
}


def run_guards(project, target_state: ProjectState) -> None:
    guards = TRANSITION_GUARDS.get(target_state, [])
    for guard in guards:
        guard(project)
