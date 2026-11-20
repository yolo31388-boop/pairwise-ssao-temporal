import math

def downsample_depth(values):
    """深度下采样。"""
    raise NotImplementedError("TODO: downsample_depth")

def reconstruct_normal(dx, dy):
    """法线重建。"""
    raise NotImplementedError("TODO: reconstruct_normal")

def reproject(uv, motion):
    """时域重投影。"""
    raise NotImplementedError("TODO: reproject")

def edge_weight(delta, threshold):
    """双边保边。"""
    raise NotImplementedError("TODO: edge_weight")

def linearize_depth(depth, near, far):
    """深度线性化。"""
    raise NotImplementedError("TODO: linearize_depth")

def ao_multiply(ao, direct):
    """AO 合成。"""
    raise NotImplementedError("TODO: ao_multiply")

def history_weight(frame):
    """历史权重。"""
    raise NotImplementedError("TODO: history_weight")

def transparent_depth(alpha):
    """透明深度写入。"""
    raise NotImplementedError("TODO: transparent_depth")

def bilateral_radius(world, pixel_scale):
    """双边半径。"""
    raise NotImplementedError("TODO: bilateral_radius")

def clamp01(value):
    """AO 钳制。"""
    raise NotImplementedError("TODO: clamp01")

def uv_valid(uv):
    """UV 合法性。"""
    raise NotImplementedError("TODO: uv_valid")

def reset_history(cut):
    """切镜重置。"""
    raise NotImplementedError("TODO: reset_history")

def kernel_basis(right):
    """采样基。"""
    raise NotImplementedError("TODO: kernel_basis")

def ssao_id(seed, index):
    """AO id。"""
    raise NotImplementedError("TODO: ssao_id")

def depth_ratio(depth, near, far):
    """深度比例。"""
    raise NotImplementedError("TODO: depth_ratio")
