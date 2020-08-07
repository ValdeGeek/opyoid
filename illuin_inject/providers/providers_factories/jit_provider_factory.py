from illuin_inject.bindings import SelfBinding
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .from_binding_provider_factory import FromBindingProviderFactory
from .provider_factory import ProviderFactory


class JitProviderFactory(ProviderFactory):
    def __init__(self):
        self.provider_factory = FromBindingProviderFactory()

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return state.options.auto_bindings

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        return self.provider_factory.create_from_binding(SelfBinding(target.type, annotation=target.annotation), state)