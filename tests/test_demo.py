import py
import pytest

@pytest.mark.moztrap(10392)
@pytest.mark.xfail(reason='demo')
@pytest.mark.parametrize('param', [1, 2, 3, 4])
def test_demo_parameterized_with_multiple_outcomes(param):
    if param == 1:
        assert True
    elif param == 2:
        assert False, 'explanation'
    elif param == 3:
        pytest.skip("we do not like threes")
    elif param == 4:
        pytest.xfail("four is a four letter word")
        assert False

@pytest.mark.moztrap(10393)
@pytest.mark.xfail(reason="demo")
@pytest.mark.parametrize('param', [1, 2])
def test_demo_xpass_trumps_xfail(param):
    if param == 1:
        assert False
    elif param == 2:
        pass
