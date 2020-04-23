# import pytest


class TestBasic:
    def test_environment(self):
        x = "this"
        print('Hello pytest!')
        assert "h" in x
