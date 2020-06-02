from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT


class FromInstanceProvider(Provider[InjectedT]):
    def __init__(self, instance: InjectedT) -> None:
        self._instance = instance

    def get(self) -> InjectedT:
        return self._instance
