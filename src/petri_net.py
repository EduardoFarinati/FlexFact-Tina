from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Union


@dataclass
class Place:
    """Representation of a Petri net place, with its number of tokens."""

    name: str
    tokens: int


@dataclass
class Arc:
    """Representation of an arc."""

    place: Place
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

    def is_met(self) -> bool:
        """Check if the arc preconditions are met."""
        if self.type == InputArcTypes.INHIBITOR:
            return self.place.tokens < self.weight

        return self.place.tokens >= self.weight


@dataclass
class Transition:
    """Representation of a tina arrow or equivalent
    Includes the conditions required to move.
    """

    name: str
    input_arcs: List[InputArc] = field(default_factory=list)
    output_arcs: List[OutputArc] = field(default_factory=list)

    def is_enabled(self) -> bool:
        """Check if the transition is enabled, by checking each arc
        preconditions are met (ie. if there are enough tokens
        present at the source place)."""

        for input_arc in self.input_arcs:
            if not input_arc.is_met():
                return False

        return True


@dataclass
class PetriNet:
    places: List[Place]
    transitions: List[Transition]

    def __init__(
        self,
        places: Union[List[Place], None] = None,
        transitions: Union[List[Transition], None] = None,
    ):
        if places is None:
            places = []
        if transitions is None:
            transitions = []

        self.places = places
        self.transitions = transitions

        # Set mapping from places and transitions
        self._place_mapping = {place.name: i for i, place in enumerate(places)}
        self._transition_mapping = {
            transition.name: i for i, transition in enumerate(transitions)
        }

    def add_place(self, place: Place):
        i = self._place_mapping.get(place.name)
        if i:
            # Overwrites place if it is
            # already added in the network
            self.places[i] = place
        else:
            self._place_mapping[place.name] = len(self.places)
            self.places.append(place)

    def add_transition(self, transition: Transition):
        i = self._transition_mapping.get(transition.name)
        if i:
            # Overwrites transition if it is
            # already added in the network
            self.transitions[i] = transition
        else:
            self._transition_mapping[transition.name] = len(self.transitions)
            self.transitions.append(transition)

    def get_place(self, name: str) -> Union[Place, None]:
        i = self._place_mapping.get(name)
        if i:
            return self.places[i]
        return None

    def get_transition(self, name: str) -> Union[Transition, None]:
        i = self._transition_mapping.get(name)
        if i:
            return self.transitions[i]
        return None

    def get_marking(self) -> List[int]:
        return [place.tokens for place in self.places]
