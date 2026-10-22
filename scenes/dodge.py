from vpython import *
# 장애물 피하기: ← → 로 움직여 떨어지는 공 5개를 피한다. 부딪히면 R 키로 다시 시작.
# 방향키를 놓고 있으면 자동 회피가 대신 움직인다.
# 키가 안 먹으면 장면을 한 번 클릭해 포커스를 준다.
# glowscript.org에 붙여 넣을 때는 맨 윗줄에 `Web VPython 3.2`를 추가한다.
#
# ── 설계 기록 ─────────────────────────────────────────
# 객체 목록   : 플레이어 구 1, 장애물 구 5(리스트), 좌우 벽 2, 바닥 1, 점수판 label 1
# 필요한 변수 : X_MAX(이동 한계), TOP·BOTTOM(장애물이 생기고 빠지는 높이),
#               PLAYER_SPEED, score, running(진행 여부), obstacles(리스트), 장애물별 speed
# 한 단계     : ① 눌린 키로 플레이어 이동(키가 없으면 자동 회피) → 벽 안쪽으로 범위 제한
#               ② for로 장애물마다 낙하 → 중심 거리 < 반지름 합이면 충돌
#               ③ 바닥 아래로 빠진 장애물은 점수 +1, 위쪽으로 옮겨 재사용
#               ④ 점수판 갱신
# 종료 조건   : 플레이어와 어느 장애물이든 중심 거리 < 두 반지름의 합 → running = False
# 초기화 상태 : 플레이어 위치·색, 장애물 위치·속도, score, running, 점수판 문구
# 심화 선택   : 점수별 난이도. 피한 개수가 늘수록 새로 떨어지는 공이 빨라진다.

scene.title = "장애물 피하기  ← →  이동 · R 다시 시작"
scene.width, scene.height = 700, 700
scene.background = vector(0.08, 0.09, 0.13)
scene.center = vector(0, 0.5, 0)
scene.range = 6
scene.userspin = False                       # 방향키·드래그로 카메라가 돌지 않게 고정
scene.userzoom = False

X_MAX = 5.0                                  # 벽 안쪽 경계
TOP, BOTTOM = 7.5, -6.5                      # 화면 위 바깥에서 생겨 아래 바깥으로 빠진다
PLAYER_Y = -4.5
PLAYER_SPEED = 8                             # 초당 이동 거리
N_OBSTACLES = 5
dt = 1 / 60

# ── 무대 ──────────────────────────────────────────────
for side in [-1, 1]:
    box(pos=vector(side * (X_MAX + 0.1), 0.5, 0), size=vector(0.2, 11.4, 0.6), color=color.gray(0.35))
box(pos=vector(0, PLAYER_Y - 0.6, 0), size=vector(2 * X_MAX + 0.4, 0.2, 0.6), color=color.gray(0.35))

player = sphere(pos=vector(0, PLAYER_Y, 0), radius=0.5, color=color.cyan)

obstacles = []
for i in range(N_OBSTACLES):
    obstacles.append(sphere(radius=0.35 + 0.25 * random(), color=color.orange))

board = label(pos=vector(0, 5.6, 0), box=False, height=18, color=color.white)

score = 0
running = True

# 지금 눌린 키 목록. 로컬 vpython의 keysdown()은 마우스가 화면 위에 있을 때만
# 갱신되므로, 키 이벤트를 직접 받아 관리한다.
pressed = []


def on_key(evt):
    if evt.event == "keydown":
        if evt.key not in pressed:
            pressed.append(evt.key)
    elif evt.key in pressed:
        pressed.remove(evt.key)


scene.bind("keydown keyup", on_key)


def fall_speed():
    """점수별 난이도: 기본 3, 피할 때마다 0.25씩 빨라지고 12에서 멈춘다."""
    return min(3 + 0.25 * score, 12)


def drop_from_top(ob, extra_height):
    """장애물을 새로 만들지 않고 위쪽으로 옮겨 재사용한다."""
    limit = X_MAX - ob.radius
    ob.pos = vector(-limit + 2 * limit * random(), TOP + extra_height, 0)
    ob.speed = fall_speed() * (0.8 + 0.4 * random())


def hit(a, b):
    """두 구가 닿는 기준: 중심 사이 거리 < 두 반지름의 합."""
    return mag(a.pos - b.pos) < a.radius + b.radius


# ── 자동 회피: 시공간 격자 탐색 ───────────────────────
# 이미 떨어지고 있는 공은 앞으로 어디 있을지 정해져 있다. 그래서 앞으로 PLAN_STEPS 프레임 동안
# "한 프레임에 왼쪽·제자리·오른쪽 한 칸"씩 움직이는 모든 경로를 격자로 깔고, 마지막 프레임부터
# 거꾸로 "이 칸에서 끝까지 살아남을 수 있나, 얼마나 여유 있게"를 채운다(동적 계획법).
# 한 칸 = 한 프레임 이동 거리라서 격자 위 경로는 실제로 움직일 수 있는 경로와 정확히 같다.
PLAN_STEPS = 60                              # 1초 앞까지 내다본다
SAFETY = 0.02                                # 충돌 판정에 더하는 여유
CLEAR_CAP = 1.5                              # 이 거리 넘게 떨어지면 여유 점수는 더 오르지 않는다
CLEAR_WEIGHT = 0.02                          # 공과 벌린 거리에 주는 점수(프레임마다)
CENTER_WEIGHT = 0.1                          # 계획 끝에서 가운데일수록 주는 점수: 다음 공에 대비
DEATH = 10000                                # 충돌 벌점. 늦게 부딪히는 경로일수록 덜 나쁘다


def blocked_spans(k):
    """k프레임 뒤 플레이어 높이에서 공들이 막는 x 구간 목록 [[왼쪽, 오른쪽], ...]"""
    spans = []
    for ob in obstacles:
        reach = player.radius + ob.radius + SAFETY
        dy = ob.pos.y - ob.speed * dt * k - PLAYER_Y
        if abs(dy) < reach:                  # 공이 플레이어 높이를 지나는 중
            half = sqrt(reach * reach - dy * dy)
            spans.append([ob.pos.x - half, ob.pos.x + half])
    return spans


def auto_direction():
    """이번 프레임에 움직일 방향: -1 왼쪽, 0 제자리, 1 오른쪽"""
    limit = X_MAX - player.radius
    w = PLAYER_SPEED * dt                    # 한 칸 = 한 프레임 이동 거리
    here = int((player.pos.x + limit) / w)   # 지금 위치의 칸 번호
    n = here + int((limit - player.pos.x) / w) + 1
    xs = []
    value = []
    for j in range(n):
        xs.append(player.pos.x + (j - here) * w)
        value.append(-CENTER_WEIGHT * abs(xs[j]))
    for k in range(PLAN_STEPS, 0, -1):       # 마지막 프레임부터 거꾸로
        spans = blocked_spans(k)
        later = value
        value = []
        for j in range(n):
            if abs(j - here) > k:            # k프레임 안에 닿을 수 없는 칸은 계산하지 않는다
                value.append(-1e18)
                continue
            gap = CLEAR_CAP
            for s in spans:
                if s[0] < xs[j] and xs[j] < s[1]:
                    gap = -1
                    break
                gap = min(gap, s[0] - xs[j] if xs[j] <= s[0] else xs[j] - s[1])
            if gap < 0:
                value.append(-DEATH * (PLAN_STEPS + 1 - k))
            else:
                best = later[j]
                if j > 0 and later[j - 1] > best:
                    best = later[j - 1]
                if j < n - 1 and later[j + 1] > best:
                    best = later[j + 1]
                value.append(best + CLEAR_WEIGHT * gap)
    # value는 이제 1프레임 뒤 각 칸의 점수. 지금 칸에서 갈 수 있는 세 칸 중 고르되 같으면 제자리
    best_d = 0
    for d in [-1, 1]:
        j = here + d
        if 0 <= j and j < n and value[j] > value[here + best_d] + 1e-9:
            best_d = d
    return best_d


def reset_game():
    global score, running
    score = 0
    running = True
    player.pos = vector(0, PLAYER_Y, 0)
    player.color = color.cyan
    for i in range(N_OBSTACLES):
        drop_from_top(obstacles[i], i * 2.4)  # 높이를 엇갈려 한꺼번에 떨어지지 않게
    board.text = "점수 0"


reset_game()

while True:
    rate(60)
    if not running:                          # 진행 여부를 매 단계 확인한다
        if "r" in pressed or "R" in pressed:
            reset_game()
        continue

    # ① 이동과 범위 제한
    manual = "left" in pressed or "right" in pressed
    if "left" in pressed:
        player.pos.x -= PLAYER_SPEED * dt
    if "right" in pressed:
        player.pos.x += PLAYER_SPEED * dt
    if not manual:                           # 손을 떼면 자동 회피
        player.pos.x += auto_direction() * PLAYER_SPEED * dt
    limit = X_MAX - player.radius
    player.pos.x = max(-limit, min(limit, player.pos.x))

    # ②③ 장애물: 낙하 → 충돌 판정 → 피했으면 점수 후 재배치
    for ob in obstacles:
        ob.pos.y -= ob.speed * dt
        if hit(player, ob):
            running = False
            player.color = color.red
            board.text = "충돌! 최종 점수 " + str(score) + "\nR 키로 다시 시작"
            break
        if ob.pos.y < BOTTOM:
            score += 1
            drop_from_top(ob, 0)

    # ④ 점수판
    if running:
        text = "점수 " + str(score) + "   속도 " + str(round(fall_speed(), 1)) + ("" if manual else "   [자동]")
        if text != board.text:               # 바뀔 때만 보내 매 프레임 통신을 줄인다
            board.text = text
