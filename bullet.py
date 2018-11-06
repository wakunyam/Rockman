from pico2d import *
import game_world
import game_framework

PIXEL_PER_METER = (32.0 / 1.7)
RUN_SPEED_KMPH = 25.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = RUN_SPEED_MPS * PIXEL_PER_METER


class Bullet:
    image = None
    hero_x = 0

    def __init__(self, x, y, velocity):
        if Bullet.image == None:
            Bullet.image = load_image('Bullet.png')
        self.x, self.y, self.velocity = x, y, velocity
        global hero_x
        hero_x = x

    def draw(self):
        self.image.clip_composite_draw(24, 172, 8, 6, 0, '', self.x, self.y, 8, 6)

    def update(self):
        global hero_x
        self.x += self.velocity * game_framework.frame_time
        if self.x < hero_x - 50 * PIXEL_PER_METER or self.x > hero_x + 50 * PIXEL_PER_METER:
            game_world.remove_object(self)