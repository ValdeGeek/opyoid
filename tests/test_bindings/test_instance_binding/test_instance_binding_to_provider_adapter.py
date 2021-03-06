import unittest
from unittest.mock import create_autospec

from opyoid import InstanceBinding, Provider, ProviderBinding, SelfBinding
from opyoid.bindings import BindingRegistry, InstanceBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator


class MyType:
    def __init__(self):
        pass


class TestInstanceBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = InstanceBindingToProviderAdapter()
        self.providers_creator = create_autospec(ProviderCreator, spec_set=True)
        self.instance = MyType()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )

    def test_accept_instance_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(InstanceBinding(MyType, MyType()), self.state))

    def test_accept_non_instance_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(SelfBinding(MyType), self.state))
        self.assertFalse(self.adapter.accept(ProviderBinding(MyType, create_autospec(Provider)), self.state))

    def test_create_returns_provider(self):
        provider = self.adapter.create(RegisteredBinding(InstanceBinding(MyType, self.instance)),
                                       self.providers_creator)

        instance = provider.get()
        self.assertIs(instance, self.instance)
