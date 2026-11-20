import pytest
from render import ssao_temporal as mod

CASES = [
    ("down", 'm.downsample_depth([0.8, 0.3, 0.5]) == 0.3'),
    ("normal", 'm.reconstruct_normal(1, 0) == approx((-0.707107, 0.0, 0.707107))'),
    ("reproj", 'm.reproject((0.5, 0.6), (0.1, 0.2)) == approx((0.4, 0.4))'),
    ("edge", 'm.edge_weight(0.1, 0.2) == 1.0'),
    ("edge2", 'm.edge_weight(0.3, 0.2) == 0.0'),
    ("linear", 'm.linearize_depth(0.5, 1, 10) == approx(1.818182)'),
    ("ao", 'm.ao_multiply(0.5, 0.8) == approx(0.4)'),
    ("history", 'm.history_weight(3) == approx(0.25)'),
    ("transparent", 'm.transparent_depth(0.5) is False'),
    ("radius", 'm.bilateral_radius(2, 3) == 6'),
    ("clamp", 'm.clamp01(-1) == 0.0'),
    ("uv", 'm.uv_valid((0.5, 0.5)) is True'),
    ("reset", 'm.reset_history(True) is True'),
    ("basis", 'm.kernel_basis((1, 0)) == (1, 0)'),
    ("id", 'm.ssao_id(3, 2) == "3:2"')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
