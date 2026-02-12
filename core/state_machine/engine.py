from core.state_machine.states import ProjectState
from core.state_machine.transitions import is_valid_transition
from core.state_machine.guards import run_guards
from core.errors import InvalidStateTransition


def transition(project, target_state: ProjectState) -> None:
    """Transition a project to a new state, enforcing validity and guards."""
    if not is_valid_transition(project.state, target_state):
        raise InvalidStateTransition(project.state, target_state)

    run_guards(project, target_state)
    project.state = target_state


def transition_to_error(project) -> None:
    """Force-transition a project to ERROR state. Always allowed."""
    project.state = ProjectState.ERROR
