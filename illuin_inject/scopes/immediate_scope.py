from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .singleton_scope import SingletonScope


class ImmediateScope(SingletonScope):
    """Always provides the same instance, objects are instantiated immediately."""

    @classmethod
    def get_scoped_provider(cls, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        provider = SingletonScope.get_scoped_provider(inner_provider)
        provider.get()
        return provider
