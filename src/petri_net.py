from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import chain
from typing import List, Union, Self


class Tokens(int):
    """Amount of tokens in a Petri net, must be positive or zero."""

    def __new__(cls, value, *args, **kwargs):
        if value < 0:
            raise ValueError("Amount of tokens must positive or zero.")
        return super().__new__(cls, value, *args, **kwargs)

    def __add__(self, other: Self):
        return self.__class__(super().__add__(other))

    def __sub__(self, other: Self):
        return self.__class__(super().__sub__(other))

    def __mul__(self, _):
        raise ValueError("Multiplication of tokens is not defined.")

    def __div__(self, _):
        raise ValueError("Division of tokens is not defined.")


@dataclass
class Place:
    """Representation of a Petri net place, with its number of tokens."""

    name: str
    tokens: Tokens


@dataclass
class Arc(ABC):
    """Representation of an arc."""

    place: Place
    weight: Tokens

    @abstractmethod
    def move_tokens(self):
        pass


@dataclass
class OutputArc(Arc):
    """Representation of an output arc."""

    def move_tokens(self):
        """Adds tokens to the output place."""
        self.place.tokens += self.weight


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

    def move_tokens(self):
        """Removes tokens from the input place."""
        if self.type == InputArcTypes.REGULAR:
            self.place.tokens -= self.weight


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

    def force_fire(self):
        """Fire the transition, moving it's tokens around. Should only
        be called when the transition is enabled."""
        for arc in chain(self.input_arcs, self.output_arcs):
            arc.move_tokens()

    def try_fire(self) -> bool:
        """Try to fire the transition, indicating it's triggering event
        has occurred. If the trasition is enabled, it's tokens are
        then moved around accordingly."""
        if not self.is_enabled():
            return False

        self.force_fire()
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
        if i is not None:
            # Overwrites place if it is already present in the network
            self.places[i] = place
        else:
            self._place_mapping[place.name] = len(self.places)
            self.places.append(place)

    def add_transition(self, transition: Transition):
        i = self._transition_mapping.get(transition.name)
        if i is not None:
            # Overwrites transition if it is already present in the network
            self.transitions[i] = transition
        else:
            self._transition_mapping[transition.name] = len(self.transitions)
            self.transitions.append(transition)

    def get_place(self, name: str) -> Union[Place, None]:
        i = self._place_mapping.get(name)
        if i is None:
            return None

        return self.places[i]

    def get_transition(self, name: str) -> Union[Transition, None]:
        i = self._transition_mapping.get(name)
        if i is None:
            return None

        return self.transitions[i]

    def get_marking(self) -> List[int]:
        return [place.tokens for place in self.places]
