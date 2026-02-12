class CoreError(Exception):
    """Base exception for all core errors."""


class InvalidStateTransition(CoreError):
    """Raised when a state transition is not allowed."""

    def __init__(self, current_state, target_state):
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"Cannot transition from {current_state.value} to {target_state.value}"
        )


class AILimitExceeded(CoreError):
    """Raised when a user has exhausted their AI usage quota."""

    def __init__(self, action: str, plan_type: str):
        self.action = action
        self.plan_type = plan_type
        super().__init__(
            f"AI limit exceeded for {action} on {plan_type} plan"
        )


class AIRateLimited(CoreError):
    """Raised when AI calls are being made too frequently (global)."""

    def __init__(self):
        super().__init__("AI rate limit exceeded. Try again later.")


class AICooldownActive(CoreError):
    """Raised when the per-user cooldown between AI calls hasn't elapsed."""

    def __init__(self, seconds_remaining: float):
        self.seconds_remaining = seconds_remaining
        super().__init__(
            f"AI cooldown active. Wait {seconds_remaining:.0f} seconds."
        )


class AIGenerationError(CoreError):
    """Raised when an AI generation call fails."""

    def __init__(self, stage: str, detail: str = ""):
        self.stage = stage
        self.detail = detail
        msg = f"AI generation failed at {stage}"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class AIValidationError(CoreError):
    """Raised when AI output fails validation."""

    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__(
            f"AI output validation failed: {'; '.join(issues)}"
        )


class GuardFailure(CoreError):
    """Raised when a state transition guard condition is not met."""

    def __init__(self, guard_name: str, reason: str):
        self.guard_name = guard_name
        self.reason = reason
        super().__init__(f"Guard '{guard_name}' failed: {reason}")
