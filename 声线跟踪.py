import math

# =========================
# 1. 基本参数
# =========================
abc = 212  # 学号后三位

# 往返时间：0.06abc 和 0.16abc
T_round_1 = 0.06 + abc / 100000.0   # 0.06212 s
T_round_2 = 0.16 + abc / 100000.0   # 0.16212 s

# 10 m 层离散后的声速剖面
# 第1层 0~10 m，第2层 10~20 m，...，第11层 100~110 m
c_list = [1520, 1519, 1518, 1517, 1516,
          1517, 1518, 1519, 1520, 1521, 1522]

dz = 10.0                    # 每层厚度，m
theta0_deg = 30.0            # 初始入射角，deg
                             # 水面掠射角60°，入射角 = 90° - 60° = 30°

# Snell 常数：sin(theta_i) / c_i = sin(theta_0) / c_0
k = math.sin(math.radians(theta0_deg)) / c_list[0]

# =========================
# 2. 计算每一完整层参数
# =========================
layers = []
t_cum = 0.0
x_cum = 0.0
z_cum = 0.0

for i, c in enumerate(c_list, start=1):
    s = k * c                    # sin(theta_i)
    theta = math.asin(s)         # 入射角，rad
    cos_t = math.cos(theta)      # cos(theta_i)

    dx = dz * s / cos_t          # 该完整层水平偏移
    dt = dz / (c * cos_t)        # 该完整层单程传播时间

    t_cum += dt
    x_cum += dx
    z_cum += dz

    layers.append({
        "i": i,
        "c": c,
        "theta_deg": math.degrees(theta),
        "s": s,
        "cos": cos_t,
        "dx": dx,
        "dt": dt,
        "dz": dz,
        "t_cum": t_cum,
        "x_cum": x_cum,
        "z_cum": z_cum
    })

# =========================
# 3. 声线跟踪函数
# =========================
def trace(t_one_way):
    """
    按层内常声速法追踪声线。
    输入：单程传播时间 t_one_way，s
    输出：总水平偏移 X、总垂向偏移 Z 及部分层信息
    """
    t_acc = 0.0
    x_acc = 0.0
    z_acc = 0.0

    for L in layers:
        # 若该层可以完整走完
        if t_one_way >= t_acc + L["dt"] - 1e-15:
            t_acc += L["dt"]
            x_acc += L["dx"]
            z_acc += L["dz"]
        else:
            # 否则在该层内结束
            tau = t_one_way - t_acc
            c = L["c"]
            s = L["s"]
            cos_t = L["cos"]

            dz_part = tau * c * cos_t
            dx_part = tau * c * s

            X = x_acc + dx_part
            Z = z_acc + dz_part

            return {
                "X": X,
                "Z": Z,
                "layer": L["i"],
                "tau": tau,
                "x_full": x_acc,
                "z_full": z_acc,
                "dx_part": dx_part,
                "dz_part": dz_part
            }

    # 若时间超过所有层
    return {
        "X": x_acc,
        "Z": z_acc,
        "layer": None,
        "tau": 0.0,
        "x_full": x_acc,
        "z_full": z_acc,
        "dx_part": 0.0,
        "dz_part": 0.0
    }

# =========================
# 4. 打印完整层参数表
# =========================
print("Snell 常数 k = sin(theta0)/c0 =", k)
print()
print("完整层参数表：")
print("层号  声速m/s  入射角deg    sinθ      cosθ      Δx/m       Δt/s         累计t/s")
for L in layers:
    print(f"{L['i']:2d}   {L['c']:6.0f}  {L['theta_deg']:10.4f}  "
          f"{L['s']:.6f}  {L['cos']:.6f}  {L['dx']:8.4f}  "
          f"{L['dt']:.9f}  {L['t_cum']:.9f}")

# =========================
# 5. 计算两个往返时间对应的海底脚印坐标
# =========================
for name, T_round in [("T1", T_round_1), ("T2", T_round_2)]:
    t_one_way = T_round / 2.0
    result = trace(t_one_way)

    print("\n" + "=" * 60)
    print(f"{name}: 往返时间 = {T_round:.5f} s")
    print(f"单程时间 = {t_one_way:.6f} s")
    print(f"声线结束于第 {result['layer']} 层")
    print(f"该层剩余时间 tau = {result['tau']:.9f} s")
    print(f"完整层累计：X = {result['x_full']:.4f} m, Z = {result['z_full']:.4f} m")
    print(f"部分层偏移：Δx = {result['dx_part']:.4f} m, Δz = {result['dz_part']:.4f} m")
    print(f"总偏移：X = {result['X']:.4f} m, Z = {result['Z']:.4f} m")

# =========================
# 6. 绘制 0~100 m 声线轮廓（可选）
# =========================
import matplotlib.pyplot as plt

# 解决中文显示问题（Windows 推荐 SimHei，Mac 推荐 Arial Unicode MS）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 前10层对应 0~100 m
xs = [0.0] + [L["x_cum"] for L in layers[:10]]
zs = [0.0] + [L["z_cum"] for L in layers[:10]]

fig, ax = plt.subplots(figsize=(6, 8))  # 调整画布比例，让 Y 轴显得更长

# 绘制折线图，添加标记
ax.plot(xs, zs, "-o", linewidth=2, markersize=5, color='#1f77b4', label='声线轨迹')

# 绘制网格
ax.grid(True, linestyle='--', alpha=0.7)

# 【关键设置】强制 X 轴与 Y 轴比例 1:1
ax.set_aspect('equal', adjustable='box')

# 坐标轴标签与标题
ax.set_xlabel("水平偏移 X / m", fontsize=12)
ax.set_ylabel("深度 Z / m", fontsize=12)
ax.set_title("0~100 m 声线轮廓（层内常声速法）", fontsize=14)

# 设置刻度范围和反向 Y 轴（深度向下为正）
ax.set_xlim(0,65)
ax.set_ylim(105,0)

ax.set_xticks(range(0, 61, 10))
ax.set_yticks(range(0, 101, 10))

# 显示图例
ax.legend()

# 调整布局并显示/保存
plt.tight_layout()
plt.savefig("sound_ray_0_100m.png", dpi=300) # 保存高清图，可直接插入Word
plt.show()