from pico2d import *
import game_framework
from bullet import Bullet
import game_world

PIXEL_PER_METER = (32.0 / 1.7)
RUN_SPEED_KMPH = 25.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = RUN_SPEED_MPS * PIXEL_PER_METER

TIME_PER_RUN = 0.3
RUN_PER_TIME = 1.0 / TIME_PER_RUN
FRAMES_PER_RUN = 3

RIGHT_DOWN, LEFT_DOWN, UP_DOWN, DOWN_DOWN, \
RIGHT_UP, LEFT_UP, UP_UP, DOWN_UP, ATTACK_DOWN, ATTACK_UP, SLIDING_DOWN, SLIDING_UP = range(12)

key_event_table = {
    (SDL_KEYDOWN, SDLK_RIGHT): RIGHT_DOWN,
    (SDL_KEYDOWN, SDLK_LEFT): LEFT_DOWN,
    (SDL_KEYDOWN, SDLK_UP): UP_DOWN,
    (SDL_KEYDOWN, SDLK_DOWN): DOWN_DOWN,
    (SDL_KEYUP, SDLK_RIGHT): RIGHT_UP,
    (SDL_KEYUP, SDLK_LEFT): LEFT_UP,
    (SDL_KEYUP, SDLK_UP): UP_UP,
    (SDL_KEYUP, SDLK_DOWN): DOWN_UP,
    (SDL_KEYDOWN, SDLK_z): ATTACK_DOWN,
    (SDL_KEYUP, SDLK_z): ATTACK_UP
}


class IdleState:
    time = 0
    @staticmethod
    def enter(hero, event):
        if event == RIGHT_DOWN:
            hero.velocity += RUN_SPEED_PPS
        elif event == LEFT_DOWN:
            hero.velocity -= RUN_SPEED_PPS
        elif event == RIGHT_UP:
            hero.velocity -= RUN_SPEED_PPS
        elif event == LEFT_UP:
            hero.velocity += RUN_SPEED_PPS
        global time
        time = get_time()
        hero.frame = 0
        hero.frame_change = 0
        hero.image = load_image('Idle.png')

    @staticmethod
    def exit(hero, event):
        del hero.image

    @staticmethod
    def do(hero):
        global time
        if get_time() - 4 >= time and hero.frame_change == 0:
            time = get_time()
            hero.frame = 1
            hero.frame_change = 1
        elif get_time() - 0.15 >= time and hero.frame_change == 1:
            time = get_time()
            hero.frame = 0
            hero.frame_change = 0


    @staticmethod
    def draw(hero):
        if hero.dir == RUN_SPEED_PPS:
            hero.image.clip_draw(int(hero.frame) * 32, 160, 32, 32, hero.x, hero.y)
        else:
            hero.image.clip_composite_draw(int(hero.frame) * 32, 160, 32, 32, 0, 'h', hero.x, hero.y, 32, 32)


class RunState:
    @staticmethod
    def enter(hero, event):
        if event == RIGHT_DOWN:
            hero.velocity += RUN_SPEED_PPS
        elif event == LEFT_DOWN:
            hero.velocity -= RUN_SPEED_PPS
        elif event == RIGHT_UP:
            hero.velocity -= RUN_SPEED_PPS
        elif event == LEFT_UP:
            hero.velocity += RUN_SPEED_PPS
        hero.dir = hero.velocity
        hero.frame = 0
        hero.frame_change = 0
        hero.image = load_image('Running.png')

    @staticmethod
    def exit(hero, event):
        pass

    @staticmethod
    def do(hero):
        hero.frame = (hero.frame + FRAMES_PER_RUN * RUN_PER_TIME * game_framework.frame_time) % 3
        hero.x += hero.velocity * game_framework.frame_time

    @staticmethod
    def draw(hero):
        if hero.velocity == RUN_SPEED_PPS:
            if int(hero.frame) == 0:
                hero.image.clip_draw(0, 160, 32, 32, hero.x, hero.y)
            elif int(hero.frame) == 1:
                hero.image.clip_draw(32, 160, 30, 32, hero.x, hero.y)
            else:
                hero.image.clip_draw(62, 160, 32, 32, hero.x, hero.y)
        else:
            if int(hero.frame) == 0:
                hero.image.clip_composite_draw(0, 160, 32, 32, 0, 'h', hero.x, hero.y, 32, 32)
            elif int(hero.frame) == 1:
                hero.image.clip_composite_draw(32, 160, 30, 32, 0, 'h', hero.x, hero.y, 30, 32)
            else:
                hero.image.clip_composite_draw(62, 160, 32, 32, 0, 'h', hero.x, hero.y, 32, 32)


class ShootState:
    @staticmethod
    def enter(hero, event):
        hero.image = load_image('Shoot.png')

    @staticmethod
    def exit(hero, event):
        del hero.image

    @staticmethod
    def do(hero):
        hero.shoot_bullet()
        hero.add_event(ATTACK_UP)

    @staticmethod
    def draw(hero):
        if hero.dir == RUN_SPEED_PPS:
            hero.image.clip_composite_draw(0, 0, 32, 32, 0, '', hero.x, hero.y, 32, 32)
        else:
            hero.image.clip_composite_draw(0, 0, 32, 32, 0, 'h', hero.x, hero.y, 32, 32)


class RunningShootState:
    @staticmethod
    def enter(hero):
        hero.frame = 0

    @staticmethod
    def exit(hero):
        pass

    @staticmethod
    def do(hero):
        hero.frame = (hero.frame + 1)

    @staticmethod
    def draw(hero):
        if hero.dir == 1:
            pass
        else:
            pass


class ChargingState:
    @staticmethod
    def enter(hero):
        pass

    @staticmethod
    def exit(hero):
        pass

    @staticmethod
    def do(hero):
        pass

    @staticmethod
    def draw(hero):
        pass


next_state_table = {
    IdleState: {RIGHT_DOWN: RunState, RIGHT_UP: RunState,
                LEFT_DOWN: RunState, LEFT_UP: RunState,
                ATTACK_DOWN: ShootState, ATTACK_UP: IdleState},
    RunState: {RIGHT_DOWN: IdleState, RIGHT_UP: IdleState,
               LEFT_DOWN: IdleState, LEFT_UP: IdleState,
               ATTACK_DOWN: RunningShootState},
    ShootState: {ATTACK_UP: IdleState, ATTACK_DOWN: ChargingState,
                 RIGHT_DOWN: RunningShootState, RIGHT_UP: RunningShootState,
                 LEFT_DOWN: RunningShootState, LEFT_UP: RunningShootState},
    RunningShootState: {RIGHT_DOWN: ShootState, RIGHT_UP: ShootState,
                        LEFT_DOWN: ShootState, LEFT_UP: ShootState,
                        ATTACK_UP: RunState}
}


class Hero:
    def __init__(self):
        self.x, self.y = 100, 100
        self.image = None
        self.dir = RUN_SPEED_PPS
        self.velocity = 0
        self.event_que = []
        self.cur_state = IdleState
        self.cur_state.enter(self, None)

    def shoot_bullet(self):
        bullet = Bullet(self.x, self.y, self.dir * 4)
        game_world.add_object(bullet, 1)

    def add_event(self, event):
        self.event_que.insert(0, event)

    def update(self):
        self.cur_state.do(self)
        if len(self.event_que) > 0:
            event = self.event_que.pop()
            self.cur_state.exit(self, event)
            self.cur_state = next_state_table[self.cur_state][event]
            self.cur_state.enter(self, event)

    def draw(self):
        self.cur_state.draw(self)

    def handle_event(self, event):
        if (event.type, event.key) in key_event_table:
            key_event = key_event_table[(event.type, event.key)]
            self.add_event(key_event)