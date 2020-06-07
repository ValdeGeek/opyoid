from typing import Type

from illuin_inject.bindings import ClassBinding, FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory


class TypeProviderFactory(ProviderFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_type(target.type)

    def create(self,
               target: Target[Type[InjectedT]],
               state: InjectionState) -> Provider[Type[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        binding = state.binding_registry.get_binding(new_target)
        if not binding or not isinstance(binding.raw_binding, ClassBinding):
            raise NoBindingFound(f"Could not find any binding for {target}")
        return FromInstanceProvider(binding.raw_binding.bound_type)
