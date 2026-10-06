WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
FPS           = 60
WINDOW_TITLE  = "Python Fighters - Phase 1"
BLACK = (0,0,0)
WHITE = (255,255,255)
SKY_BLUE = (135,206,235)
GROUND_BROWN = (110,70,40)
GRAY = (60,60,60)
P1_COLOR = (60,120,220)
P2_COLOR = (220,70,70)
P1_ATTACK_C = (255,230,120)
P2_ATTACK_C = (255,150,60)
HEALTH_BG = (40,40,40)
HEALTH_FG_P1 = (60,220,90)
HEALTH_FG_P2 = (235,82,95)
GROUND_Y = 600
GRAVITY = 0.9
JUMP_POWER = -20
MOVE_SPEED = 6
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 140
MAX_HEALTH = 100
ATTACK_DAMAGE = 8
ATTACK_WIDTH = 60
ATTACK_HEIGHT = 30
ATTACK_ACTIVE_TIME = 8
ATTACK_COOLDOWN = 30


# ==========================================================
# PHASE 2 -- COMBAT
# ==========================================================

# LIGHT ATTACK
LIGHT_STARTUP   = 4
LIGHT_ACTIVE    = 3
LIGHT_RECOVERY  = 6
LIGHT_DAMAGE    = 5
LIGHT_HITSTUN   = 12
LIGHT_BLOCKSTUN = 6
LIGHT_KNOCKBACK = 3
LIGHT_REACH     = 60
LIGHT_HEIGHT    = 26

# HEAVY ATTACK
HEAVY_STARTUP   = 10
HEAVY_ACTIVE    = 4
HEAVY_RECOVERY  = 16
HEAVY_DAMAGE    = 14
HEAVY_HITSTUN   = 20
HEAVY_BLOCKSTUN = 10
HEAVY_KNOCKBACK = 9
HEAVY_REACH     = 78
HEAVY_HEIGHT    = 34

# SPECIAL ATTACK (placeholder until Phase 5)
SPECIAL_STARTUP   = 14
SPECIAL_ACTIVE    = 6
SPECIAL_RECOVERY  = 22
SPECIAL_DAMAGE    = 22
SPECIAL_HITSTUN   = 26
SPECIAL_BLOCKSTUN = 14
SPECIAL_KNOCKBACK = 14
SPECIAL_REACH     = 92
SPECIAL_HEIGHT    = 50

# COMBAT FEEL
HIT_PAUSE_FRAMES = 5
BLOCK_REDUCTION  = 0.25
BLOCK_KNOCKBACK_MULT = 0.5
PARRY_WINDOW_FRAMES = 4

# HURTBOX
HURTBOX_INSET_X = 6
CROUCH_HURTBOX_RATIO = 0.55

# COMBO
COMBO_WINDOW_FRAMES = 45
COMBO_MIN_DISPLAY = 2

# KNOCKDOWN
KNOCKDOWN_FRAMES = 70
GETUP_FRAMES     = 20

# CONTROLS
P1_KEYS = {
    "left":    "a",
    "right":   "d",
    "jump":    "w",
    "crouch":  "s",
    "block":   "q",
    "light":   "j",
    "heavy":   "k",
    "special": "l",
}

P2_KEYS = {
    "left":    "LEFT",
    "right":   "RIGHT",
    "jump":    "UP",
    "crouch":  "DOWN",
    "block":   "RALT",
    "light":   "RETURN",
    "heavy":   "RSHIFT",
    "special": "RCTRL",
}


# ==========================================================
# PHASE 3.8 -- JUICE / IMPACT
# ==========================================================

# Fighter visual scale (1.0 = normal). Bigger fighters feel chunkier.
FIGHTER_SCALE = 1.55
DEBUG_HITBOXES = False

# Hit sparks
HIT_SPARK_COUNT_LIGHT = 10
HIT_SPARK_COUNT_HEAVY = 22
HIT_SPARK_COUNT_SPECIAL = 30
HIT_SPARK_LIFE = 14

# Screen shake (magnitude in pixels, duration in frames)
SHAKE_LIGHT = (4, 8)
SHAKE_HEAVY = (12, 14)
SHAKE_SPECIAL = (18, 18)
SHAKE_KO = (22, 40)

# Flash on KO
KO_FLASH_LIFE = 16

# Slow-motion on KO — how many frames after KO still update at normal speed
KO_SLOWMO_FRAMES = 22

# Bigger hit pause (chunkier feel)
HIT_PAUSE_FRAMES_LIGHT = 4
HIT_PAUSE_FRAMES_HEAVY = 7
HIT_PAUSE_FRAMES_SPECIAL = 9
