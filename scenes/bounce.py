from vpython import *
# glowscript.org(Web VPython)에 붙여 넣을 때는 맨 윗줄에 `Web VPython 3.2`를 추가한다.
# 그 외 코드는 로컬·브라우저 양쪽에서 그대로 돈다.

scene.title = "튕기는 공 — 반발계수 0.8"
scene.background = color.gray(0.15)

g = vector(0, -9.8, 0)
e = 0.8                      # 반발계수: 충돌 직후 속력 / 직전 속력
dt = 0.005

floor = box(pos=vector(0, -0.05, 0), size=vector(4, 0.1, 2), color=color.gray(0.6))
ball = sphere(pos=vector(0, 3, 0), radius=0.15, color=color.orange,
              make_trail=True, trail_radius=0.02)
ball.v = vector(0.4, 0, 0)

plot = graph(title="높이 y(t)", xtitle="t (s)", ytitle="y (m)", width=600, height=250)
height = gcurve(color=color.orange)

t = 0
while t < 8:
    rate(1 / dt)             # 실시간 재생: 초당 1/dt 프레임
    ball.v += g * dt
    ball.pos += ball.v * dt
    if ball.pos.y < ball.radius and ball.v.y < 0:
        ball.pos.y = ball.radius
        ball.v.y = -e * ball.v.y
    height.plot(t, ball.pos.y)
    t += dt
