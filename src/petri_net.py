from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List


@dataclass
class Arc:
    """Representation of an arc."""

    place: str
    weight: int
    

@dataclass
class OutputArc(Arc):
    """Representation of an output arc."""


class InputArcTypes(Enum):
    """Definition of an input arc types."""

    REGULAR = auto()
    READ = auto()
    INHIBITOR = auto()

@dataclass
class InputArc(Arc):
    """Representation of an input arc."""

    type: InputArcTypes

    def is_met(self, tokens: int) -> bool:
        """Check if the arc preconditions are met."""
        if self.type == InputArcTypes.INHIBITOR:
            return tokens < self.weight

        return tokens >= self.weight


@dataclass
class Transition:
    """Representation of a tina arrow or equivalent
    Includes the conditions required to move.
    """

    name: str
    input_arcs: List[InputArc] = field(default_factory=list)
    output_arcs: List[OutputArc] = field(default_factory=list)

    def is_enabled(self, places: Dict[str, int]) -> bool:
        """Check if the transition is enabled, by checking each arc preconditions are met
        (ie. if there are enough tokens present at the source place)."""

        for input_arc in self.input_arcs:
            tokens = places[input_arc.place]
            if not input_arc.is_met(tokens):
                return False

        return True
