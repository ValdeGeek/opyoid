import logging
from typing import Dict, List

from illuin_inject.target import Target
from .bindings import Binding
from .typings import InjectedT


class BindingRegistry:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._bindings_by_target: Dict[Target[InjectedT], List[Binding[InjectedT]]] = {}

    def register(self, binding: Binding) -> None:
        target = Target(binding.target_type, binding.annotation)
        if target not in self._bindings_by_target:
            self._bindings_by_target[target] = []
        self._bindings_by_target[target].append(binding)

    def get_bindings_by_target(self) -> Dict[Target[InjectedT], List[Binding[InjectedT]]]:
        return self._bindings_by_target

    def update(self, binding_registry: "BindingRegistry") -> None:
        for bindings in binding_registry.get_bindings_by_target().values():
            for binding in bindings:
                self.register(binding)

    def get_bindings(self, target: Target[InjectedT]) -> List[Binding]:
        if isinstance(target.type, str):
            possible_target_types = list(set(
                available_target.type
                for available_target in self._bindings_by_target
                if isinstance(available_target.type, type)
                and available_target.type.__name__ == target.type
            ))
            if len(possible_target_types) == 1:
                # noinspection PyTypeChecker
                target = Target(possible_target_types[0], target.annotation)
            elif possible_target_types:
                self.logger.error(f"Could not find binding for '{target.type}': multiple types with this name found")
        return self._bindings_by_target.get(target, [])