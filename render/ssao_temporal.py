"""SSAO 时域降噪相关的核心数学工具。

这里实现的是渲染器里那些与分辨率、相机和时序相关的约定；每一项都对应
一类已知的视觉缺陷（见各函数 docstring）。
"""

import math


def downsample_depth(values):
    """深度下采样。

    半分辨率深度图取邻域的最小深度（离相机最近的表面），而不是点采样或
    平均。平均会把细杆等薄几何和背景混在一起，轮廓处漏出亮边；取最小值
    相当于用保守的最近表面覆盖整个降采样像素，保住几何边缘。
    """
    depths = [float(v) for v in values if v is not None]
    if not depths:
        return math.inf
    return min(depths)


def reconstruct_normal(dx, dy):
    """由深度梯度重建法线。

    深度梯度指向深度增大的方向（远离相机），而表面法线与之相反，因此
    法线正比于 ``(-dx, -dy, 1)``。归一化后按朝向修正：若 z 分量为负则整体
    翻转，保证法线朝向相机。否则背面（F 面）会被算反，平面上的半球积分
    出现同心圆状伪影。
    """
    nx, ny, nz = -float(dx), -float(dy), 1.0
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0.0:
        return (0.0, 0.0, 1.0)
    normal = (nx / length, ny / length, nz / length)
    if normal[2] < 0.0:
        normal = (-normal[0], -normal[1], -normal[2])
    return normal


def reproject(uv, motion):
    """时域重投影。

    ``motion`` 是当前帧像素相对上一帧的位移（运动矢量），所以上一帧的
    采样位置是 ``uv - motion``。只用上一帧矩阵而忽略运动矢量的做法会让
    移动物体对不上历史样本，拖出灰影。调用方还应结合 :func:`uv_valid`
    与深度/法线校验决定是否接受历史。
    """
    return (float(uv[0]) - float(motion[0]), float(uv[1]) - float(motion[1]))


def edge_weight(delta, threshold):
    """双边保边。

    ``delta`` 是当前样本与中心样本的深度（或法线）差异。差异在阈值内视为
    同一表面，权重为 1；超过阈值视为边缘，权重归零，避免跨边缘模糊把
    接触阴影糊掉。
    """
    limit = abs(float(threshold))
    distance = abs(float(delta))
    if limit == 0.0:
        return 1.0 if distance == 0.0 else 0.0
    return 1.0 if distance <= limit else 0.0


def linearize_depth(depth, near, far):
    """深度线性化。

    使用标准透视投影反解：``near * far / (far - d * (far - near))``。
    这里按投影矩阵的语义正确区分近/远平面；若调用方把两者传反，自动
    交换，避免远处深度被映射成无穷大导致 AO 全白。
    """
    near, far = float(near), float(far)
    if near > far:
        near, far = far, near
    d = float(depth)
    denominator = far - d * (far - near)
    if denominator <= 0.0:
        return math.inf
    return near * far / denominator


def ao_multiply(ao, direct):
    """AO 合成。

    在线性空间把 AO 项乘到直接光上，并且只乘一次，结果钳制到 [0, 1]。
    在 sRGB 缓冲里做乘法会让暗部发灰；在 gizmo / 描边等后续 pass 再乘
    一次则会让边缘发黑。
    """
    return clamp01(float(ao) * float(direct))


def history_weight(frame):
    """历史权重。

    按时间衰减为 ``1 / (frame + 1)``，即指数滑动平均的等价写法。按帧数
    无界累加会让静止镜头的历史样本永不淘汰，噪声和偏差越积越脏。
    """
    frame = max(0, int(frame))
    return 1.0 / (frame + 1)


def transparent_depth(alpha):
    """透明深度写入。

    只有完全不透明（``alpha >= 1``）的表面才写遮挡深度。透明物体写深度
    会让玻璃后面的墙被误判为被遮挡，产生错误 AO。
    """
    return float(alpha) >= 1.0


def bilateral_radius(world, pixel_scale):
    """双边半径。

    滤波半径以世界尺度给出，再按 ``pixel_scale``（世界单位到像素的换算）
    变换到像素域。写死像素半径会让 4K 和 1080p 的降噪强度差一大截。
    """
    return abs(float(world) * float(pixel_scale))


def clamp01(value):
    """把值钳制到 [0, 1]，NaN 归零。"""
    value = float(value)
    if value != value:  # NaN
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def uv_valid(uv):
    """UV 合法性：只有落在 [0, 1] 内的重投影结果才能取历史样本。"""
    u = float(uv[0])
    v = float(uv[1])
    return 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0


def reset_history(cut):
    """切镜时重置历史，避免跨镜头复用上一帧样本。"""
    return bool(cut)


def kernel_basis(right):
    """采样基。

    半球采样核定义在相机空间；这里返回相机右向量的归一化切线，供调用方
    与法线一起构造切空间基，使 AO 随相机旋转而旋转。方向固定在屏幕空间
    会让转身后 AO 跟着转。
    """
    x = float(right[0])
    y = float(right[1])
    length = math.hypot(x, y)
    if length == 0.0:
        return (1.0, 0.0)
    return (x / length, y / length)


def ssao_id(seed, index):
    """生成稳定的 AO 采样标识，便于重投影与调试时对齐样本。"""
    return f"{seed}:{index}"


def depth_ratio(depth, near, far):
    """线性深度相对远平面的比例，用于跨帧深度一致性校验。

    越界时钳制到 [0, 1]；非法平面参数返回 0。
    """
    near, far = float(near), float(far)
    if near > far:
        near, far = far, near
    if near <= 0.0 or far <= near:
        return 0.0
    return clamp01(linearize_depth(depth, near, far) / far)
