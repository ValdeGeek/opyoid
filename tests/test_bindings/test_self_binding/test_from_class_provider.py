import unittest
from unittest.mock import create_autospec

from illuin_inject.bindings import FromClassProvider
from illuin_inject.provider import Provider


class TestFromClassProvider(unittest.TestCase):
    def test_provider_without_args(self):
        class MyType:
            def __init__(self):
                pass

        provider = FromClassProvider(MyType, [], {})
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_provider_with_args(self):
        class MyType:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        provider_1 = create_autospec(Provider)
        provider_1.get.return_value = "value_1"
        provider_2 = create_autospec(Provider)
        provider_2.get.return_value = "value_2"
        provider_3 = create_autospec(Provider)
        provider_3.get.return_value = "value_3"
        provider_4 = create_autospec(Provider)
        provider_4.get.return_value = "value_4"

        provider = FromClassProvider(MyType, [provider_1, provider_2], {"kwarg_1": provider_3, "kwarg_2": provider_4})
        instance = provider.get()
        self.assertIsInstance(instance, MyType)
        self.assertEqual(("value_1", "value_2"), instance.args)
        self.assertEqual({"kwarg_1": "value_3", "kwarg_2": "value_4"}, instance.kwargs)