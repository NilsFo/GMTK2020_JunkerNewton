import pygame

from math import floor
from datetime import datetime

import pyscroll
import pymunk
import pymunk.pygame_util
import typing

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


class Game:
    def __init__(self, screen):
        self.debug_font = pygame.font.Font("assets/fonts/FiraSans-Regular.ttf", 12)

        self.current_screen: Level = None
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
            dt = clock.tick_busy_loop(MAX_FPS)/1000


## LEVEL SCREEN


class Level:
    def __init__(self, game, map_name="test_dungeon.tmx"):
        self.game = game

        self.physspace = pymunk.Space()
        self.physspace.gravity = 0, 0

        self.world: pyscroll.BufferedRenderer = None
        self.load_map(map_name)


        self.body = pymunk.Body()
        self.body.position = (80,550)
        # Astronaut collision model
        poly = pymunk.Poly(self.body, [
            (38 - 64, 120 - 64),
            (24 - 64, 66  - 64),
            (30 - 64, 35  - 64),
            (45 - 64, 9   - 64),
            (72 - 64, 7   - 64),
            (100- 64, 58  - 64),
            (73 - 64, 120 - 64),
        ])
        poly.density = 0.005
        self.physspace.add(self.body, poly)
        sprite = EntityRenderer(pygame.image.load("assets/textures/astronaut.png"), physbody=self.body)
        sprite.add(self.group)

        # Test Asteroid
        asteroid = pymunk.Body()
        asteroid.position = (320,450)
        c = pymunk.Circle(asteroid, 27)
        c.density = 0.1
        c.friction = 0.4
        self.physspace.add(c, asteroid)
        asteroid.angular_velocity = 0.1
        EntityRenderer(pygame.image.load("assets/textures/meteor.png"), physbody=asteroid).add(self.group)

        # Add physics from map tiles
        layer = 1
        tile_size_x, tile_size_y = self.map_data.tile_size
        blocks = []
        for x, y, _ in self.map.layers[layer].tiles():
            props: typing.Dict = self.map.get_tile_properties(x, y, layer)
            if "blocked" in props.keys():
                if props["blocked"]:
                    block_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                    bb = pymunk.BB(x*tile_size_x,  # l
                                   (y+1) * tile_size_y,  # b
                                   (x+1) * tile_size_x,  # r
                                   y*tile_size_y)  # t
                    block = pymunk.Poly.create_box(block_body, (tile_size_x, tile_size_y))

                    blocks.append(block_body)
                    block_body.position = bb.center()
                    blocks.append(block)
        self.physspace.add(*blocks)

    def load_map(self, map_id):
        self.map = load_pygame("assets/maps/" + map_id)
        self.map_data = pyscroll.TiledMapData(self.map)
        self.world = pyscroll.BufferedRenderer(self.map_data, self.get_screen_size())
        self.world.zoom=2
        self.world.scroll((0,300))

        self.group = pyscroll.PyscrollGroup(map_layer=self.world)

    def update(self, dt):
        self.physspace.step(dt)
        self.group.update(dt)
        #self.world.scroll((0, 1))
        self.world.center(self.body.position)

    def render(self, surface):
        self.group.draw(surface)

    def on_resize(self):
        size = display.get_surface().get_size()
        view_center = self.world.view_rect.center
        self.world.set_size(size)
        self.world.center(view_center)

    def on_key_press(self, event):
        if event.key == pygame.K_DOWN:
            self.body.apply_impulse_at_local_point((-2000,0), (0,0))
        if event.key == pygame.K_UP:
            self.body.apply_impulse_at_local_point((2000,0), (0,0))
        if event.key == pygame.K_LEFT:
            self.body.apply_impulse_at_local_point((200,0), (30,60))
            self.body.apply_impulse_at_local_point((-200,0), (-30,-60))
        if event.key == pygame.K_RIGHT:
            self.body.apply_impulse_at_local_point((-200,0), (30,60))
            self.body.apply_impulse_at_local_point((200,0), (-30,-60))

    def on_key_release(self, event):
        pass

    def get_screen_size(self):
        return self.game.screen.get_size()

    def postprocess_render(self, screen):
        pass

    def render_ui(self, screen):
        pass

    def on_screen_enter(self):
        pass

    def on_screen_exit(self):
        pass

    def on_input_event(self, event):
        pass

    def on_ui_input_event(self, event, source):
        pass


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
        self.ticks = int(duration*1000)
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
    def __init__(self, image: pygame.Surface, physbody: pymunk.Body=None):

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
        print(self.physbody.angle)
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

    game.current_screen = Level(game)
    game.current_screen.on_screen_enter()

    print("Starting Game Loop")
    game.game_loop()
    print('Game closed. Goodbye.')


if __name__ == '__main__':
    main()
