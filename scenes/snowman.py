from vpython import *
# 눈 내리는 밤의 눈사람.
# glowscript.org에 붙여 넣을 때는 맨 윗줄에 `Web VPython 3.2`를 추가한다.

scene.title = "눈사람"
scene.width, scene.height = 900, 650
scene.background = vector(0.06, 0.08, 0.16)       # 남색 밤하늘
scene.ambient = color.gray(0.35)
scene.center = vector(0, 2.1, 0)
scene.forward = vector(0, -0.22, -1)
scene.range = 3.4
distant_light(direction=vector(-0.3, 1, 0.25), color=color.gray(0.35))   # 위에서 내리는 달빛

SNOW = vector(0.96, 0.97, 1.0)
COAL = color.gray(0.08)
WOOD = vector(0.40, 0.24, 0.11)
RED = vector(0.80, 0.10, 0.15)

# ── 땅과 배경 ─────────────────────────────────────────
cylinder(pos=vector(0, -0.06, 0), axis=vector(0, 0.06, 0), radius=9, color=vector(0.90, 0.93, 1.0), shininess=0.05)
for x, z, s in [(-2.6, 1.2, 0.9), (2.4, 0.6, 1.2), (-1.4, -2.2, 1.4), (3.2, -2.6, 1.0)]:
    ellipsoid(pos=vector(x, -0.04, z), size=vector(s * 1.6, s * 0.35, s * 1.2), color=SNOW, shininess=0.1)   # 눈 둔덕

def pine(x, z, h):
    cylinder(pos=vector(x, 0, z), axis=vector(0, h * 0.18, 0), radius=h * 0.05, color=WOOD)
    for i in range(3):                              # 아래층일수록 넓은 원뿔 3단
        base = h * (0.15 + 0.25 * i)
        cone(pos=vector(x, base, z), axis=vector(0, h * (0.45 - 0.07 * i), 0),
             radius=h * (0.32 - 0.07 * i), color=vector(0.07, 0.30, 0.18))

for x, z, h in [(-4.2, -4.5, 3.2), (-2.4, -6.0, 3.8), (3.0, -5.2, 3.5), (4.8, -3.8, 2.6), (0.8, -7.0, 4.2)]:
    pine(x, z, h)

sphere(pos=vector(-5, 7.5, -12), radius=0.7, color=vector(1, 0.96, 0.82), emissive=True)   # 달

# ── 몸통 세 덩이: 겹치게 쌓아 이음매를 숨긴다 ───────────
ellipsoid(pos=vector(0, 0.90, 0), size=vector(2.1, 1.9, 2.1), color=SNOW, shininess=0.15)   # 반지름 1.05 / 0.95
ellipsoid(pos=vector(0, 2.35, 0), size=vector(1.5, 1.4, 1.5), color=SNOW, shininess=0.15)   # 반지름 0.75 / 0.70
HEAD_C, HEAD_R = vector(0, 3.45, 0), 0.5
sphere(pos=HEAD_C, radius=HEAD_R, color=SNOW, shininess=0.15)

# ── 얼굴 ──────────────────────────────────────────────
for sx in [-1, 1]:
    sphere(pos=HEAD_C + 0.48 * norm(vector(sx * 0.18, 0.15, 0.45)), radius=0.06, color=COAL)
cone(pos=HEAD_C + vector(0, 0.02, 0.45), axis=vector(0.02, -0.04, 0.45), radius=0.075,
     color=vector(1.0, 0.50, 0.10))                 # 당근 코
for i in range(5):                                  # 석탄 다섯 알로 웃는 입
    mx = -0.2 + 0.1 * i
    my = -0.22 + 2 * mx * mx
    mz = sqrt(HEAD_R ** 2 - mx * mx - my * my)
    sphere(pos=HEAD_C + vector(mx, my, mz), radius=0.035, color=COAL)

# ── 단추: 가운데 덩이 표면 위에 박는다 ─────────────────
for dy in [0.3, 0.0, -0.3]:
    z = 0.75 * sqrt(1 - (dy / 0.70) ** 2)
    sphere(pos=vector(0, 2.35 + dy, z), radius=0.06, color=COAL)

# ── 나뭇가지 팔 ───────────────────────────────────────
def arm(start, direction, length):
    d = norm(direction)
    cylinder(pos=start, axis=d * length, radius=0.035, color=WOOD)
    tip = start + d * length
    for twist in [-0.55, 0.55]:                     # 끝에서 갈라지는 손가락 두 개
        f = norm(d + vector(0, twist, twist * 0.3))
        cylinder(pos=tip, axis=f * 0.28, radius=0.022, color=WOOD)
    mid = start + d * length * 0.55                 # 중간의 잔가지
    cylinder(pos=mid, axis=norm(d + vector(0, 0.9, 0)) * 0.25, radius=0.02, color=WOOD)

arm(vector(-0.68, 2.50, 0), vector(-1, 0.45, 0.1), 1.15)
arm(vector(0.68, 2.50, 0), vector(1, 0.95, 0.15), 1.10)   # 오른팔은 손 흔들기

# ── 목도리 ────────────────────────────────────────────
ring(pos=vector(0, 3.02, 0), axis=vector(0, 1, 0), radius=0.31, thickness=0.09, color=RED)
p1, p2 = vector(0.20, 2.98, 0.38), vector(0.30, 2.40, 0.90)
box(pos=(p1 + p2) / 2, axis=p2 - p1, up=vector(0, 0.4, 0.48),
    size=vector(mag(p2 - p1), 0.04, 0.17), color=RED)

# ── 모자: 오른쪽으로 9° 기울인 축 하나에 세 부품을 꿴다 ───
tilt = radians(9)
up_hat = vector(sin(tilt), cos(tilt), 0)
base = vector(-0.04, 3.86, 0)
cylinder(pos=base, axis=0.05 * up_hat, radius=0.55, color=COAL)                       # 챙
cylinder(pos=base + 0.03 * up_hat, axis=0.55 * up_hat, radius=0.33, color=COAL)       # 몸체
cylinder(pos=base + 0.07 * up_hat, axis=0.12 * up_hat, radius=0.335, color=RED)       # 띠

# ── 내리는 눈 ─────────────────────────────────────────
TOP, N = 8.0, 220
flakes = []
for i in range(N):
    f = sphere(pos=vector(12 * random() - 6, TOP * random(), 9 * random() - 6),
               radius=0.025 + 0.02 * random(), color=color.white, emissive=True)
    f.speed = 0.5 + 0.6 * random()                  # 크기마다 다른 낙하 속도
    f.phase = 2 * pi * random()                     # 좌우 흔들림 위상
    flakes.append(f)

t, dt = 0, 1 / 30
while True:
    rate(30)
    t += dt
    for f in flakes:
        f.pos.y -= f.speed * dt
        f.pos.x += 0.15 * sin(1.5 * t + f.phase) * dt
        if f.pos.y < 0:
            f.pos.y = TOP
