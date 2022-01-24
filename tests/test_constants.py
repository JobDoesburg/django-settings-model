from django.test import TestCase
from constants.constants import Constants as RegisteredConstants
from constants.models import Constant


class ConstantsTests(TestCase):

    def setUp(self):
        self.constants = RegisteredConstants()

    def test_add_constant_type_str(self):
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())
        self.constants.register_constant("test-constant", Constant.TYPE_STR, False, default_value="test")
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertEqual(Constant.objects.get(slug="test-constant").get_value(), "test")

    def test_add_constant_type_int(self):
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())
        self.constants.register_constant("test-constant", Constant.TYPE_INT, False, default_value=100)
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertEqual(Constant.objects.get(slug="test-constant").get_value(), 100)

    def test_add_constant_type_float(self):
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, False, default_value=100.12345)
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertEqual(Constant.objects.get(slug="test-constant").get_value(), 100.12345)

    def test_add_constant_nullable(self):
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())
        self.constants.register_constant("test-constant", Constant.TYPE_STR, True)
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertIsNone(Constant.objects.get(slug="test-constant").get_value())

    def test_add_constant_type_str_null_default_value(self):
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())
        self.constants.register_constant("test-constant", Constant.TYPE_STR, True, default_value="Bla")
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertEqual(Constant.objects.get(slug="test-constant").get_value(), "Bla")

    def test_add_constant_wrong_type_value(self):
        def call_add_constant():
            self.constants.register_constant("test-constant", Constant.TYPE_INT, False, default_value="Bla")

        self.assertRaises(TypeError, call_add_constant)

    def test_add_constant_twice(self):
        self.constants.register_constant("test-constant", Constant.TYPE_INT, False, default_value=1)

        def add_constant_second_time():
            self.constants.register_constant("test-constant", Constant.TYPE_INT, False, default_value=2)
        self.assertRaises(Exception, add_constant_second_time)
        self.assertTrue(Constant.objects.filter(slug="test-constant").exists())
        self.assertEqual(Constant.objects.get(slug="test-constant").get_value(), 1)

    def test_add_constant_non_nullable_no_default_value(self):
        def add_constant_non_nullable():
            self.constants.register_constant("test-constant", Constant.TYPE_INT, False)
        self.assertRaises(Exception, add_constant_non_nullable)
        self.assertFalse(Constant.objects.filter(slug="test-constant").exists())

    def test_add_constant_already_in_db(self):
        constant = Constant.objects.create(slug="test-constant", type=Constant.TYPE_INT, value=1, nullable=False)
        self.constants.register_constant("test-constant", Constant.TYPE_INT, False, default_value=1)
        self.assertEqual(constant.id, self.constants.get_constant("test-constant").id)

    def test_add_constant_already_in_db_different_type(self):
        Constant.objects.create(slug="test-constant", type=Constant.TYPE_INT, value=1, nullable=False)
        self.constants.register_constant("test-constant", Constant.TYPE_STR, False, default_value="Bla")
        self.assertEqual(self.constants.get_value("test-constant"), "Bla")

    def test_change_constant_nullable_true_false(self):
        Constant.objects.create(slug="test-constant", type=Constant.TYPE_FLOAT, value=3.14, nullable=True)
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, False, default_value=2.13)
        self.assertEqual(self.constants.get_value("test-constant"), 3.14)
        self.assertFalse(Constant.objects.get(slug="test-constant").nullable)

    def test_change_constant_nullable_true_false_default_value(self):
        Constant.objects.create(slug="test-constant", type=Constant.TYPE_FLOAT, value=None, nullable=True)
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, False, default_value=2.13)
        self.assertEqual(self.constants.get_value("test-constant"), 2.13)
        self.assertFalse(Constant.objects.get(slug="test-constant").nullable)

    def test_change_constant_nullable_false_true(self):
        Constant.objects.create(slug="test-constant", type=Constant.TYPE_FLOAT, value=3.14, nullable=False)
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, True, default_value=2.13)
        self.assertEqual(self.constants.get_value("test-constant"), 3.14)
        self.assertTrue(Constant.objects.get(slug="test-constant").nullable)

    def test_set_value(self):
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, False, default_value=12345.6789)
        self.constants.set_value("test-constant", 9876.54321)
        self.assertEqual(self.constants.get_value("test-constant"), 9876.54321)

    def test_set_value_wrong_type(self):
        self.constants.register_constant("test-constant", Constant.TYPE_FLOAT, False, default_value=12345.6789)

        def set_value_wrong_type():
            self.constants.set_value("test-constant", 9876)

        self.assertRaises(TypeError, set_value_wrong_type)

    def test_constant_not_registered(self):
        def not_registered_constant():
            self.constants.get_constant("not-registered")

        self.assertRaises(ValueError, not_registered_constant)

    def test_forcefully_removed_constant(self):
        self.constants.register_constant("forcefully-removed", Constant.TYPE_INT, False, default_value=123)

        def forcefully_removed_constant():
            self.constants.get_constant("forcefully-removed")

        Constant.objects.get(slug="forcefully-removed").delete()
        self.assertRaises(Exception, forcefully_removed_constant)

    def test_registered(self):
        self.constants.register_constant("registered", Constant.TYPE_INT, False, default_value=123)
        Constant.objects.create(slug="not-registered", type=Constant.TYPE_INT, nullable=False, value=123)
        self.assertTrue(self.constants.is_registered("registered"))
        self.assertFalse(self.constants.is_registered("not-registered"))