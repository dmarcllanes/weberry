from core.state_machine.states import ProjectState

# All valid state transitions
VALID_TRANSITIONS: dict[ProjectState, list[ProjectState]] = {
    ProjectState.DRAFT: [ProjectState.INPUT_READY],
    ProjectState.INPUT_READY: [ProjectState.MEMORY_READY],
    ProjectState.MEMORY_READY: [ProjectState.PLAN_READY, ProjectState.SITE_GENERATED],
    ProjectState.PLAN_READY: [ProjectState.PLAN_APPROVED],
    ProjectState.PLAN_APPROVED: [ProjectState.SITE_GENERATED],
    ProjectState.SITE_GENERATED: [ProjectState.PREVIEW],
    ProjectState.PREVIEW: [ProjectState.PUBLISHED],
    ProjectState.PUBLISHED: [],
    ProjectState.ERROR: [ProjectState.DRAFT],
}

# Transitions that involve AI calls
AI_TRANSITIONS: dict[ProjectState, str] = {
    ProjectState.MEMORY_READY: "planner",
    ProjectState.PLAN_APPROVED: "generation",
}


def is_valid_transition(current: ProjectState, target: ProjectState) -> bool:
    return target in VALID_TRANSITIONS.get(current, [])


def get_ai_action(current_state: ProjectState) -> str | None:
    return AI_TRANSITIONS.get(current_state)
