"""Minimal pixel-based Geometry Dash environment interface."""

from .environment import (
    ACTION_CONTRACT_VERSION,
    ENVIRONMENT_VERSION,
    OBSERVATION_CONTRACT_VERSION,
    REWARD_CONTRACT_VERSION,
    EmergencyStop,
    GeometryDashEnv,
)
from .state_machine import ScreenState, StateMachine, StateTransitionError

__all__ = [
    "ACTION_CONTRACT_VERSION",
    "ENVIRONMENT_VERSION",
    "OBSERVATION_CONTRACT_VERSION",
    "REWARD_CONTRACT_VERSION",
    "EmergencyStop",
    "GeometryDashEnv",
    "ScreenState",
    "StateMachine",
    "StateTransitionError",
]
