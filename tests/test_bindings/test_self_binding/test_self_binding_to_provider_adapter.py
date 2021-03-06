import unittest
from typing import List
from unittest.mock import call, create_autospec

from opyoid import ClassBinding, InstanceBinding, PerLookupScope, Provider, ProviderBinding, SelfBinding, \
    SingletonScope, ThreadScope, named_arg
from opyoid.bindings import BindingRegistry, FromClassProvider, SelfBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.scopes.thread_scoped_provider import ThreadScopedProvider
from opyoid.target import Target


class MyType:
    def __init__(self):
        pass


class TestSelfBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SelfBindingToProviderAdapter()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.context = InjectionContext(Target(MyType), self.state)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_accept_self_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(SelfBinding(MyType), self.context))

    def test_accept_non_self_binding_returns_false(self):
        class MySubType(MyType):
            pass

        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType()), self.context))
        self.assertFalse(self.adapter.accept(ClassBinding(MyType, MySubType), self.context))
        self.assertFalse(self.adapter.accept(ProviderBinding(MyType, create_autospec(Provider)), self.context))

    def test_create_provider_without_args(self):
        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyType)), self.context)

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(SingletonScope)),
        )
        self.assertIsInstance(provider, FromClassProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_default_constructor(self):
        class MyOtherType:
            pass

        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(SingletonScope)),
        )
        self.assertIsInstance(provider, FromClassProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)

    def test_create_scoped_provider(self):
        mock_scope_provider = create_autospec(Provider, spec_set=True)
        mock_scope_provider.get.return_value = ThreadScope()
        self.state.provider_creator.get_provider.return_value = mock_scope_provider
        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyType, scope=ThreadScope)), self.context)

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(ThreadScope)))

        self.assertIsInstance(provider, ThreadScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_parameters(self):
        class MyOtherType:
            def __init__(self, arg_1: str, arg_2: int, *args: float, arg_3: bool, **kwargs):
                self.args = [arg_1, arg_2, *args]
                self.kwargs = {
                    "arg_3": arg_3,
                    **kwargs,
                }

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"
        mock_provider_2 = create_autospec(Provider)
        mock_provider_2.get.return_value = 2
        mock_provider_3 = create_autospec(Provider)
        mock_provider_3.get.return_value = [1.2, 3.4]
        mock_provider_4 = create_autospec(Provider)
        mock_provider_4.get.return_value = True

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            mock_provider_2,
            mock_provider_3,
            mock_provider_4,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(["my_arg_1", 2, 1.2, 3.4], instance.args)
        self.assertEqual({"arg_3": True}, instance.kwargs)
        self.assertEqual([
            call(self.context.get_child_context(Target(str, "arg_1"))),
            call(self.context.get_child_context(Target(int, "arg_2"))),
            call(self.context.get_child_context(Target(List[float], "args"))),
            call(self.context.get_child_context(Target(bool, "arg_3"))),
            call(self.context.get_child_context(Target(SingletonScope))),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_from_named_binding(self):
        class MyOtherType:
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(
            RegisteredBinding(SelfBinding(MyOtherType, named="my_name")), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(self.context.get_child_context(Target(str, "arg"))),
            call(self.context.get_child_context(Target(str))),
            call(self.context.get_child_context(Target(SingletonScope))),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_named_positional_argument(self):
        class MyOtherType:
            @named_arg("arg", "my_name")
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(self.context.get_child_context(Target(str, "my_name"))),
            call(self.context.get_child_context(Target(SingletonScope))),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_named_args(self):
        class MyOtherType:
            @named_arg("arg", "my_name")
            def __init__(self, *arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = ["my_arg_1"]

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(("my_arg_1",), instance.arg)
        self.assertEqual([
            call(self.context.get_child_context(Target(List[str], "my_name"))),
            call(self.context.get_child_context(Target(SingletonScope))),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_missing_parameters_raises_exception(self):
        class MyOtherType:
            def __init__(self, arg: str) -> None:
                self.arg = arg

            self.state.provider_creator.get_provider.side_effect = NoBindingFound

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)

    def test_create_provider_with_default_parameter(self):
        class MyOtherType:
            def __init__(self, arg: str = "default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            NoBindingFound,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_without_type_hint(self):
        class MyOtherType:
            def __init__(self, arg="default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType)), self.context)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_non_injectable_scope_raises_exception(self):
        self.state.provider_creator.get_provider.side_effect = NoBindingFound()

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(RegisteredBinding(SelfBinding(MyType)), self.context)
