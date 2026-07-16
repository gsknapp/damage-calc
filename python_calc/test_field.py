import unittest

from python_calc.field import Field, Side


class FieldSideTests(unittest.TestCase):
    def test_side_supports_common_flags(self) -> None:
        side = Side(isReflect=True, isTailwind=True)
        self.assertTrue(side.isReflect)
        self.assertTrue(side.isTailwind)

    def test_field_normalizes_side_dicts(self) -> None:
        field = Field(
            attackerSide={'isReflect': True, 'isTailwind': True},
            defenderSide={'isLightScreen': True},
        )
        self.assertIsInstance(field.attackerSide, Side)
        self.assertTrue(field.attackerSide.isReflect)
        self.assertTrue(field.attackerSide.isTailwind)
        self.assertTrue(field.defenderSide.isLightScreen)


if __name__ == '__main__':
    unittest.main()
