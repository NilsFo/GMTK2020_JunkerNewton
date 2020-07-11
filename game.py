import os
import typing
from datetime import datetime
from math import floor
import random

import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
import pyscroll
from pygame.sprite import Sprite
from pytmx import load_pygame

from interpolation import *

pygame.init()

MAX_FPS = 60
screen_width = 1500
screen_height = floor(screen_width / (16 / 9))

black = 0, 0, 0

display = pygame.display
main_screen: pygame.Surface = display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Junker Newton")

gmtk_font = "assets/fonts/FiraSans-Regular.ttf"

ui_font = pygame.font.Font(gmtk_font, 30)

class Game:
    def __init__(self, screen):
        self.debug_font = pygame.font.Font(gmtk_font, 12)

        self.current_screen: BaseLevel = None
        self.screen: pygame.Surface = screen

    def setup(self):
        pass

    def game_loop(self):
        # Timing
        clock = pygame.time.Clock()
        dt = 1 / MAX_FPS

        # Lets run this thing
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # sys.exit()
                    running = False
                    continue

                self.current_screen.on_input_event(event)

                if event.type == pygame.KEYDOWN:
                    self.current_screen.on_key_press(event)

                if event.type == pygame.KEYUP:
                    self.current_screen.on_key_release(event)

                if event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    pygame.display.set_caption("MORTAL CONGA (" + str(event.w) + "x" + str(event.h) + ")")

                    if self.current_screen is not None:
                        self.current_screen.on_resize()

            # There should always be a 'current_screen'. That's the currently displayed screen.
            self.current_screen.update(dt)
            self.screen.fill(black)

            self.current_screen.render(self.screen)
            self.current_screen.postprocess_render(self.screen)
            self.current_screen.render_ui(self.screen)

            # Showing debug messages
            self.screen.blit(self.debug_font.render(str(clock.get_fps()), True, (255, 255, 255)), (5, 5))
            message_list = get_all_debug_messages()
            for i in range(len(message_list)):
                msg = message_list[i]
                self.screen.blit(self.debug_font.render(msg, True, (255, 255, 255)), (5, 15 + 15 * i))
            debug_messages_apply_delta_time(dt)

            pygame.display.flip()
            dt = clock.tick_busy_loop(MAX_FPS) / 1000


## LEVEL SCREEN


collision_types = {
    "object": 0,
    "astronaut": 1,
    "collectible": 2
}


class BaseLevel:
    def __init__(self, game, map_name="test_dungeon.tmx"):
        self.game = game

        self.physspace = pymunk.Space()
        self.physspace.gravity = 0, 0

        self.btn_accelerate_img = None
        self.btn_decelerate_img = None
        self.btn_left_img = None
        self.btn_right_img = None

        self.world: pyscroll.BufferedRenderer = None
        self.load_map(map_name)

        self.astronaut = pymunk.Body()

        # Astronaut collision model
        poly = pymunk.Poly(self.astronaut, [
            (38 - 64, 120 - 64),
            (24 - 64, 66 - 64),
            (30 - 64, 35 - 64),
            (45 - 64, 9 - 64),
            (72 - 64, 7 - 64),
            (100 - 64, 58 - 64),
            (73 - 64, 120 - 64),
        ])
        poly.density = 0.005
        poly.collision_type = collision_types["astronaut"]
        self.physspace.add(self.astronaut, poly)
        sprite = EntityRenderer(pygame.image.load("assets/textures/astronaut.png"), physbody=self.astronaut)
        sprite.add(self.group)

        self.astronaut_state = {}

        # Add physics from map tiles
        layer = 1
        tile_size_x, tile_size_y = self.map_data.tile_size
        blocks = []
        for x, y, _ in self.map.layers[layer].tiles():
            props: typing.Dict = self.map.get_tile_properties(x, y, layer)
            if "blocked" in props.keys():
                if props["blocked"]:
                    block_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                    bb = pymunk.BB(x * tile_size_x,  # l
                                   (y + 1) * tile_size_y,  # b
                                   (x + 1) * tile_size_x,  # r
                                   y * tile_size_y)  # t
                    block = pymunk.Poly.create_box(block_body, (tile_size_x, tile_size_y))

                    blocks.append(block_body)
                    block_body.position = bb.center()
                    blocks.append(block)
        self.physspace.add(*blocks)

        self.win_trigger = pymunk.BB(10,10,200,200)

        self.button_queue = []
        self.button_group = pygame.sprite.Group()
        for i in range(4):
            bt = ControlButton(self,random.randint(0,3),self.get_button_x(i))
            self.button_queue.append(bt)
            self.button_group.add(bt)

    def load_map(self, map_id):
        self.map = load_pygame("assets/maps/" + map_id)
        self.map_data = pyscroll.TiledMapData(self.map)
        self.world = pyscroll.BufferedRenderer(self.map_data, self.get_screen_size())
        self.world.zoom = 2
        self.world.scroll((0, 300))

        # Loading buttons
        btn = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_down.png")
        self.btn_accelerate_img = pygame.transform.scale(btn, np.array(btn.get_size()) * 3)
        btn = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_up.png")
        self.btn_decelerate_img = pygame.transform.scale(btn, np.array(btn.get_size()) * 3)
        btn = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_left.png")
        self.btn_left_img = pygame.transform.scale(btn, np.array(btn.get_size()) * 3)
        btn = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_right.png")
        self.btn_right_img = pygame.transform.scale(btn, np.array(btn.get_size()) * 3)

        self.group = pyscroll.PyscrollGroup(map_layer=self.world)

    def update(self, dt):
        self.physspace.step(dt)
        self.group.update(dt)
        self.button_group.update(dt)

        # self.world.scroll((0, 1))
        self.world.center(self.astronaut.position)

        if self.check_win_condition():
            print("A winner is you!")


    def render(self, surface):
        self.group.draw(surface)

    def on_resize(self):
        size = display.get_surface().get_size()
        view_center = self.world.view_rect.center
        self.world.set_size(size)
        self.world.center(view_center)

    def on_key_press(self, event):
        if event.key == pygame.K_DOWN:
            self.astronaut.apply_impulse_at_local_point((-2000,0), (0,0))
        if event.key == pygame.K_UP:
            self.astronaut.apply_impulse_at_local_point((2000,0), (0,0))
        if event.key == pygame.K_LEFT:
            self.astronaut.apply_impulse_at_local_point((200,0), (30,60))
            self.astronaut.apply_impulse_at_local_point((-200,0), (-30,-60))
        if event.key == pygame.K_RIGHT:
            self.astronaut.apply_impulse_at_local_point((-200,0), (30,60))
            self.astronaut.apply_impulse_at_local_point((200,0), (-30,-60))

        #Num keys 1-4: 49-51
        print('Key event: '+str(event.key))
        if event.key == 49:
            self.on_control_button_pressed(0)
        if event.key == 50:
            self.on_control_button_pressed(1)
        if event.key == 51:
            self.on_control_button_pressed(2)
        if event.key == 52:
            self.on_control_button_pressed(3)

    def on_control_button_pressed(self,index):
        bt = self.button_queue[index]
        if bt is None:
            return

        if bt.type==0:
            self.astronaut.apply_impulse_at_local_point((-2000,0), (0,0))
        if bt.type==3:
            self.astronaut.apply_impulse_at_local_point((2000,0), (0,0))
        if bt.type==1:
            self.astronaut.apply_impulse_at_local_point((200,0), (30,60))
            self.astronaut.apply_impulse_at_local_point((-200,0), (-30,-60))
        if bt.type==2:
            self.astronaut.apply_impulse_at_local_point((-200,0), (30,60))
            self.astronaut.apply_impulse_at_local_point((200,0), (-30,-60))

        bt.on_execute()
        self.button_queue[index] = None
        self.button_group.remove(bt)

    def check_win_condition(self):
        return self.win_trigger.contains_vect(self.astronaut.position)

    def on_key_release(self, event):
        pass

    def get_screen_size(self):
        return self.game.screen.get_size()

    def postprocess_render(self, screen):
        pass

    def render_ui(self, screen):
        w, h = self.get_screen_size()
        bw, bh = self.btn_right_img.get_size()

        # Drawing conveyor background
        pygame.draw.rect(screen, black, (self.get_button_x(0)-30, h-bh-30, self.get_button_x(4)-self.get_button_x(0)+60-8, h))

        # Drawing debug target
        pygame.draw.line(screen,(255,255,255),(0,h/2),(w,h/2))
        pygame.draw.line(screen,(255,255,255),(w/2,0),(w/2,h))

        # Drawing buttons
        for i in range(4):
            bx = self.get_button_x(i)
            #screen.blit(self.btn_right_img, (bx, h - bh))
            hotkey_text = ui_font.render(str(i+1),False,(255,255,255))
            screen.blit(hotkey_text,(bx,h-bh-32))

        self.button_group.draw(screen)

    def get_button_x(self, index):
        w, h = self.get_screen_size()
        bw, bh = self.btn_right_img.get_size()
        button_offset = 6
        bw = bw + button_offset*2

        return (w / 2) - (bw*2) + (button_offset) + (bw * index)

    def get_button_ui_width(self):
        return self.get_button_x(1)-self.get_button_x(0)

    def on_screen_enter(self):
        pass

    def on_screen_exit(self):
        pass

    def on_input_event(self, event):
        pass

    def on_ui_input_event(self, event, source):
        pass


class TestLevel(BaseLevel):
    def __init__(self, game, map_name="test_dungeon.tmx"):

        super().__init__(game)

        self.astronaut.position = (80, 550)
        self.astronaut_state["has_mcguffin"] = False

        # Test Asteroid
        asteroid = pymunk.Body()
        asteroid.position = (320,450)
        c = pymunk.Circle(asteroid, 27)
        c.density = 0.1
        c.friction = 0.4
        c.collision_type = collision_types["collectible"]
        self.physspace.add(c, asteroid)
        asteroid.angular_velocity = 0.1
        EntityRenderer(pygame.image.load("assets/textures/meteor.png"), physbody=asteroid).add(self.group)


        def collect(arbiter, space, data):
            collectible = arbiter.shapes[1]
            space.remove(collectible, collectible.body)
            associated_sprites = filter(lambda s: collectible in s.physbody.shapes, self.group.sprites())
            self.group.remove(*associated_sprites)
            self.astronaut_state["has_mcguffin"] = True
            return False

        handler = self.physspace.add_collision_handler(collision_types["astronaut"], collision_types["collectible"])
        handler.pre_solve = collect

    def check_win_condition(self):
        return super().check_win_condition() and self.astronaut_state["has_mcguffin"]

class Animation2D:
    def __init__(self,
                 vector_from: typing.Tuple[float, float],
                 vector_to: typing.Tuple[float, float],
                 duration: float,
                 interpolation: typing.Union[Interpolation, typing.Tuple[Interpolation]] = Linear(),
                 start_immediately=True):

        super().__init__()
        self.vector_from = vector_from
        self.vector_to = vector_to
        self.ticks = int(duration * 1000)
        if isinstance(interpolation, Interpolation):
            self.interpolation_x = interpolation
            self.interpolation_y = interpolation
        else:
            self.interpolation_x = interpolation[0]
            self.interpolation_y = interpolation[1]

        self.started = False
        self.paused = False
        self.finished = False

        self._t = 0
        self._p = 0

        self.update_listeners = []
        self.started_listeners = []
        self.finished_listeners = []

        if start_immediately:
            self.start()

    def start(self):
        self.started = True
        if self.paused:
            self.paused = False
        else:
            self.on_animation_started()

    def pause(self):
        self.paused = False

    def stop(self):
        self.finished = True
        self.on_animation_finished()

    def update(self, dt):
        if self.is_active():
            self._t += dt
            if self._t > self.ticks:
                self._t = self.ticks
                self.finished = True
                self.on_animation_finished()

            self._p = self._t / self.ticks

    def end(self):
        self._t = self.ticks
        self._p = 1
        self.on_animation_finished()

    def get_animation_x(self) -> float:
        return self.interpolation_x.interpolate(self.vector_from[0], self.vector_to[0], self._p)

    def get_animation_y(self) -> float:
        return self.interpolation_y.interpolate(self.vector_from[1], self.vector_to[1], self._p)

    def is_finished(self):
        return self.finished

    def is_active(self) -> bool:
        return self.started and not self.finished and not self.paused

    def add_animation_updated_callback(self, fun):
        self.update_listeners.append(fun)

    def add_animation_finished_callback(self, fun):
        self.finished_listeners.append(fun)

    def add_animation_started_callback(self, fun):
        self.started_listeners.append(fun)

    def on_animation_updated(self):
        for l in self.update_listeners:
            l()

    def on_animation_finished(self):
        for l in self.finished_listeners:
            l()

    def on_animation_started(self):
        for l in self.started_listeners:
            l()


class EntityRenderer(Sprite):
    def __init__(self, image: pygame.Surface, physbody: pymunk.Body = None):

        super().__init__()

        self._sprite_x = 0
        self._sprite_y = 0
        self.physbody = physbody
        self.src_image = image
        self.image = image
        self.rect: pygame.Rect = image.get_rect()

        self.animations: typing.List[Animation2D] = []

    def update(self, dt):
        super().update(dt)

        if self.physbody:
            self._sprite_x, self._sprite_y = self.physbody.position

        if self.animations:
            for anim in self.animations:
                anim.update(dt)

                # Is the animation done?
                if anim.is_finished():
                    # If yes, remove the animation and apply any permanent movement
                    self.animations.remove(anim)

                    # TODO maybe temporary animations that reset?
                    self._sprite_x += anim.get_animation_x()
                    self._sprite_y += anim.get_animation_y()

            # Add all animation movement
            self.rect.x = self._sprite_x + sum(map(lambda a: a.get_animation_x(), self.animations))
            self.rect.y = self._sprite_y + sum(map(lambda a: a.get_animation_y(), self.animations))
        else:
            self.rect.x = self._sprite_x
            self.rect.y = self._sprite_y

        self.image = pygame.transform.rotate(self.src_image, -math.degrees(self.physbody.angle))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = int(self._sprite_x), int(self._sprite_y)

    def set_sprite_position(self, x=None, y=None, stop_animations=True):
        if x is not None:
            self._sprite_x = x
        if y is not None:
            self._sprite_y = y

        if stop_animations:
            self.stop_animations()

    def get_sprite_position_x(self):
        return self._sprite_x + sum(map(lambda a: a.get_animation_x(), self.animations))

    def get_sprite_position_y(self):
        return self._sprite_y + sum(map(lambda a: a.get_animation_y(), self.animations))

    def stop_animations(self, reset_position=False):
        for anim in self.animations:
            anim.stop()
            if not reset_position:
                self._sprite_x += anim.get_animation_x()
                self._sprite_y += anim.get_animation_y()
        self.animations.clear()

    def is_animation_active(self):
        return len(self.animations) > 0

    def animate(self, animation: Animation2D):
        self.animations.append(animation)

class AnimatedEntity(Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)

        self._sprite_x = 0
        self._sprite_y = 0
        self.image = None
        self.rect: pygame.Rect = None

        self.animations: typing.List[Animation2D] = []

    def update(self, dt):
        super().update(dt)

        if self.animations:
            for anim in self.animations:
                anim.update(dt)

                # Is the animation done?
                if anim.is_finished():
                    # If yes, remove the animation and apply any permanent movement
                    self.animations.remove(anim)

                    # TODO maybe temporary animations that reset?
                    self._sprite_x += anim.get_animation_x()
                    self._sprite_y += anim.get_animation_y()

            # Add all animation movement
            self.rect.x = self._sprite_x + sum(map(lambda a: a.get_animation_x(), self.animations))
            self.rect.y = self._sprite_y + sum(map(lambda a: a.get_animation_y(), self.animations))
        else:
            self.rect.x = self._sprite_x
            self.rect.y = self._sprite_y


    def set_sprite_position(self, x=None, y=None, stop_animations=True):
        if x is not None:
            self._sprite_x = x
        if y is not None:
            self._sprite_y = y

        if stop_animations:
            self.stop_animations()

    def get_sprite_position_x(self):
        return self._sprite_x + sum(map(lambda a: a.get_animation_x(), self.animations))

    def get_sprite_position_y(self):
        return self._sprite_y + sum(map(lambda a: a.get_animation_y(), self.animations))

    def stop_animations(self, reset_position=False):
        for anim in self.animations:
            anim.stop()
            if not reset_position:
                self._sprite_x += anim.get_animation_x()
                self._sprite_y += anim.get_animation_y()
        self.animations.clear()

    def is_animation_active(self):
        return len(self.animations) > 0

    def animate(self, animation: Animation2D):
        self.animations.append(animation)

class ControlButton(AnimatedEntity):

    def __init__(self, level, type:int, x):
        super().__init__()
        self.level=level
        self.type = type
        w,h = level.get_screen_size()

        if type==0:
            self.image=level.btn_decelerate_img
        if type==1:
            self.image=level.btn_left_img
        if type==2:
            self.image=level.btn_right_img
        if type==3:
            self.image=level.btn_accelerate_img
        self.rect: pygame.Rect = self.image.get_rect()

        sw,sh = self.image.get_size()
        self._sprite_x = x
        self._sprite_y = h-sh

    def on_execute(self):
        pass

    def update(self, dt):
        super().update(dt)



### DEBUG MESSAGES
_debug_message_list = []
debug_message_default_time = 5000


def display_debug_message(msg: str, time=debug_message_default_time):
    msg = '[' + gct() + '] ' + msg.strip()
    _debug_message_list.append((msg, time))
    print(msg)


def get_all_debug_messages():
    ret = []
    for i in range(len(_debug_message_list)):
        ret.append(_debug_message_list[i][0])

    return ret


def debug_messages_apply_delta_time(dt):
    temp_list = _debug_message_list.copy()
    _debug_message_list.clear()

    for i in range(len(temp_list)):
        msg = temp_list[i][0]
        time = temp_list[i][1]
        time -= dt

        if time > 0:
            _debug_message_list.append((msg, time))


def gct():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def main():
    global game
    print("Loading")
    game = Game(main_screen)
    game.setup()
    print("Finished loading")

    game.current_screen = TestLevel(game)
    game.current_screen.on_screen_enter()

    print("Starting Game Loop")
    game.game_loop()
    print('Game closed. Goodbye.')


if __name__ == '__main__':
    main()
