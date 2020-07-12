import os
import random
import typing
from datetime import datetime
from math import floor
import pygame_gui
from pygame_gui import UIManager

import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
import pyscroll
from pygame.sprite import Sprite
from pytmx import load_pygame

import interpolation
from interpolation import *

pygame.init()

debug_mode = True

MAX_FPS = 60
screen_width = 1500
screen_height = floor(screen_width / (16 / 9))
_update_time = 1.0 / 60.0
key_escape = 27

black = (0, 0, 0)
white = (0, 0, 0)

countdown_intervals = [8,10,12,14]

display = pygame.display
main_screen: pygame.Surface = display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Junker Newton")

gmtk_font = "assets/fonts/FiraSans-Light.ttf"

ui_font_8 = pygame.font.Font(gmtk_font, 8)
ui_font_12 = pygame.font.Font(gmtk_font, 12)
ui_font_15 = pygame.font.Font(gmtk_font, 15)
ui_font_18 = pygame.font.Font(gmtk_font, 18)
ui_font_21 = pygame.font.Font(gmtk_font, 21)
ui_font_24 = pygame.font.Font(gmtk_font, 24)
ui_font_48 = pygame.font.Font(gmtk_font, 48)
ui_font_64 = pygame.font.Font(gmtk_font, 64)
ui_font_72 = pygame.font.Font(gmtk_font, 72)
ui_font_128 = pygame.font.Font(gmtk_font, 128)

## ASSETS
mm_background = pygame.image.load("assets/background/background.jpg")
black_hole_bg = pygame.image.load("assets/textures/bh_visualization.jpg")
img_astronaut = pygame.image.load("assets/textures/astronaut/astronaut.png")
img_astronaut_sat = pygame.image.load("assets/textures/astronaut/astronaut-sat.png")
img_astronaut_tb = pygame.image.load("assets/textures/astronaut/astronaut-tb.png")
img_astronaut_tb_sat = pygame.image.load("assets/textures/astronaut/astronaut-tb-sat.png")
img_astronaut_tf = pygame.image.load("assets/textures/astronaut/astronaut-tf.png")
img_astronaut_tf_sat = pygame.image.load("assets/textures/astronaut/astronaut-tf-sat.png")
img_astronaut_tl = pygame.image.load("assets/textures/astronaut/astronaut-tl.png")
img_astronaut_tl_sat = pygame.image.load("assets/textures/astronaut/astronaut-tl-sat.png")
img_astronaut_tr = pygame.image.load("assets/textures/astronaut/astronaut-tr.png")
img_astronaut_tr_sat = pygame.image.load("assets/textures/astronaut/astronaut-tr-sat.png")

# LOADING ACTIVE BUTTONS
btn_accelerate_img = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_down1.png")
btn_accelerate_img = pygame.transform.scale(btn_accelerate_img, np.array(btn_accelerate_img.get_size()) * 3)
btn_decelerate_img = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_up1.png")
btn_decelerate_img = pygame.transform.scale(btn_decelerate_img, np.array(btn_decelerate_img.get_size()) * 3)
btn_left_img = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_left1.png")
btn_left_img = pygame.transform.scale(btn_left_img, np.array(btn_left_img.get_size()) * 3)
btn_right_img = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_right1.png")
btn_right_img = pygame.transform.scale(btn_right_img, np.array(btn_right_img.get_size()) * 3)

# LOADING DISABLED BUTTONS
btn_accelerate_img_disabled = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_down2.png")
btn_accelerate_img_disabled = pygame.transform.scale(btn_accelerate_img_disabled, np.array(btn_accelerate_img_disabled.get_size()) * 3)
btn_decelerate_img_disabled = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_up2.png")
btn_decelerate_img_disabled = pygame.transform.scale(btn_decelerate_img_disabled, np.array(btn_decelerate_img_disabled.get_size()) * 3)
btn_left_img_disabled = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_left2.png")
btn_left_img_disabled = pygame.transform.scale(btn_left_img_disabled, np.array(btn_left_img_disabled.get_size()) * 3)
btn_right_img_disabled = pygame.image.load("assets" + os.sep + "textures" + os.sep + "button" + os.sep + "btn_rot_right2.png")
btn_right_img_disabled = pygame.transform.scale(btn_right_img_disabled, np.array(btn_right_img_disabled.get_size()) * 3)

# Credits
f = open("assets/credits.txt")
credits = f.readlines()
f.close()

# Sound & Music
pygame.mixer.init()
snd_bump_light = pygame.mixer.Sound("assets/sounds/bump_light.wav")
snd_bump_hard = pygame.mixer.Sound("assets/sounds/bump_hard.wav")
snd_bump_light.set_volume(0.3)
snd_bump_hard.set_volume(0.3)
snd_jet1 = pygame.mixer.Sound("assets/sounds/jet1_wet.wav")
snd_jet2 = pygame.mixer.Sound("assets/sounds/jet2_wet.wav")
snd_jet1.set_volume(0.2)
snd_jet2.set_volume(0.2)

pygame.mixer.set_num_channels(2)
mixer_bump_channel = pygame.mixer.Channel(1)

class Game:
    def __init__(self, screen):
        self.debug_font = pygame.font.Font(gmtk_font, 25)

        self.current_screen: BaseLevel = None
        self.next_screen:Screen = None
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
            if self.next_screen:
                print("Going to the next screen!")
                self.current_screen.on_screen_exit()
                # self.next_screen.parent_screen = self.current_screen
                self.current_screen = self.next_screen
                self.current_screen.on_screen_enter()
                self.next_screen = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # sys.exit()
                    running = False
                    continue

                self.current_screen.on_input_event(event)

                if event.type == pygame.KEYDOWN:
                    self.current_screen.on_key_press(event)

                    if event.key == key_escape:
                        self.current_screen.on_key_escape(event)

                if event.type == pygame.KEYUP:
                    self.current_screen.on_key_release(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_screen.on_mouse_release(event)

                if event.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    pygame.display.set_caption("Junker Newton")

                    if self.current_screen is not None:
                        self.current_screen.on_resize()

            # There should always be a 'current_screen'. That's the currently displayed screen.
            self.current_screen.update(dt)
            self.screen.fill(black)

            self.current_screen.render(self.screen)
            self.current_screen.postprocess_render(self.screen)
            self.current_screen.render_ui(self.screen)

            # Showing debug messages
            fps_surface = self.debug_font.render('FPS: '+str(clock.get_fps()), True, (255, 255, 255))
            fw, fh = fps_surface.get_size()
            self.screen.blit(fps_surface, (5, 5))

            message_list = get_all_debug_messages()
            for i in range(len(message_list)):
                msg = message_list[i]
                self.screen.blit(self.debug_font.render(msg, True, (255, 255, 255)), (5, fh * (i+1)))
            debug_messages_apply_delta_time(dt)

            pygame.display.flip()
            dt = clock.tick_busy_loop(MAX_FPS) / 1000

    def to_main_menu(self, first_start: bool = False):
        mn = MainMenuScreen(game)
        self.next_screen = mn

        if first_start:
            mn.on_game_startup()

## LEVEL SCREEN


collision_types = {
    "object": 0,
    "astronaut": 1,
    "collectible": 2
}

def create_button_bag():
    bag = [0,0,1,1,2,2,3,3]
    random.shuffle(bag)
    return iter(bag)

class Screen():

    def __init__(self, game, parent_screen=None):
        super().__init__()
        self.game = game
        # TODO can we remove this field?

        self.delta_time = 0
        self.ups = 0

        self.screen_shake_timer = 0
        self.screen_shake_magnitude = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.camera_zoom = 1

        self.ui_manager: pygame_gui.UIManager = None
        # A parent screen to render, in case this screen is a overlay
        self.parent_screen = parent_screen

    def update(self, dt):
        self.delta_time += dt
        if self.delta_time > _update_time:
            self.update_fixed()
            self.delta_time -= _update_time
            self.ups += 1
            #print('UPD: ' + str(self.ups) + '. Delta: ' + str(self.delta_time) + '. Dt: ' + str(dt))

        self.screen_shake_timer = max(0, self.screen_shake_timer - dt)

        self.ui_manager.update(dt)

    def update_fixed(self):
        if self.is_screen_shaking():
            self.shake_offset_x = random.randint(-self.screen_shake_magnitude, self.screen_shake_magnitude)
            self.shake_offset_y = random.randint(-self.screen_shake_magnitude, self.screen_shake_magnitude)
        pass

    def render(self, screen):
        if self.parent_screen is not None:
            self.parent_screen.render(screen)
            self.parent_screen.postprocess_render(screen)
            self.parent_screen.render_ui(screen)

    def render_ui(self, screen):
        self.ui_manager.draw_ui(screen)

    def postprocess_render(self, screen):
        # This should not be overwritten, but if you do, please call the super()
        if (self.camera_offset_x != 0 or self.camera_offset_y != 0) and self.camera_zoom == 1:
            orig_screen = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(orig_screen, (self.camera_offset_x, self.camera_offset_y))

        if self.camera_zoom != 1:
            w, h = screen.get_size()
            sx = int(w / self.camera_zoom)
            sy = int(h / self.camera_zoom)
            r = pygame.Rect(self.camera_offset_x, self.camera_offset_y, sx, sy)

            temp = pygame.Surface((sx, sy))
            temp.blit(screen, (0, 0), r)
            temp = pygame.transform.scale(temp, (w, h))

            screen.fill((0, 0, 0))
            screen.blit(temp, (0, 0))

        if self.is_screen_shaking():
            orig_screen = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(orig_screen, (self.shake_offset_x, self.shake_offset_y))

    def on_mouse_release(self,event):
        pass

    def on_key_press(self, event):
        print("Key was pressed: " + str(event.key) + " ('" + event.unicode + "')")

    def on_key_release(self, event):
        print("Key was released: " + str(event.key))

    def on_key_escape(self,event):
        pass

    def on_resize(self):
        self.init_ui()

    def on_screen_enter(self):
        self.init_ui()

    def on_screen_exit(self):
        pass

    def on_input_event(self, event):
        self.ui_manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                self.on_ui_input_event(event, event.ui_element)

    def on_ui_input_event(self, event, source):
        pass

    def init_ui(self):
        # Internal function that should not be overwritten
        w, h = pygame.display.get_surface().get_size()
        self.ui_manager = pygame_gui.UIManager((w, h))
        # self.ui_manager.set_visual_debug_mode(True)
        self.setup_ui_elements(screen_w=w, screen_h=h, manager=self.ui_manager)

    def setup_ui_elements(self, screen_w: int, screen_h: int, manager: UIManager):
        # This function should be overwritten to determine UI elements
        pass

    def set_screen_shake(self, duration_dt: int, magnitude: int):
        self.screen_shake_timer = duration_dt
        self.screen_shake_magnitude = magnitude

    def is_screen_shaking(self):
        return self.screen_shake_timer > 0

    def center_camera(self, x: int = None, y: int = None):
        # Centers the camera on a specific location, taking the zoom into account
        w, h = self.get_screen_size()
        if x is None:
            x = int(w / 2)
        if y is None:
            y = int(h / 2)

        ox = int(x - (w / self.camera_zoom) / 2)
        oy = int(y - (h / self.camera_zoom) / 2)
        self.camera_offset_y = oy
        self.camera_offset_x = ox

    def set_camera_offset(self, camera_offset_x=0, camera_offset_y=0):
        self.camera_offset_x = camera_offset_x
        self.camera_offset_y = camera_offset_y

    def reset_camera(self):
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.camera_zoom = 1

    def stop_shake(self):
        self.screen_shake_timer = 0

    def get_screen_size(self):
        return self.game.screen.get_size()

class MainMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        self.btn_story = None
        self.btn_select = None
        self.credit_lines = []

        for line in credits:
            print(line)
            self.credit_lines.append(ui_font_18.render(line, True, (255, 255, 255)))

    def render(self, screen):
        super().render(screen)
        screen.blit(mm_background,(0,0))

    def on_game_startup(self):
        display_debug_message("Welcome to JUNKER NEWTON! THANKS FOR PLAYING!",time=20)
        display_debug_message("Make sure to look up the controls before playing!",time=21)
        display_debug_message("Have fun!",time=22)
        display_debug_message("<3",time=7)

    def render_ui(self, screen):
        super().render_ui(screen)
        w,h = self.get_screen_size()
        start_x = w-350
        start_y = h-525

        i = 0
        for line in self.credit_lines:
            screen.blit(line,(start_x,start_y+28*i))
            i+=1

    def setup_ui_elements(self, screen_w: int, screen_h: int, manager: UIManager):
        super().setup_ui_elements(screen_w, screen_h, manager)

        self.btn_story = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((screen_w - 225, 50), (160, 90)),
            text='Story Mode',
            manager=manager)
        self.btn_select = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((screen_w - 225, 150), (160, 90)),
            text='Level Select',
            manager=manager)

    def on_ui_input_event(self, event, source):
        super().on_ui_input_event(event, source)
        print("A user input was made")

        if source == self.btn_story:
            self.game.next_screen = Level1(self.game)

        if source == self.btn_select:
            self.game.next_screen = Level1(self.game)


class BaseLevel(Screen):
    def __init__(self, game, map_name="test_dungeon.tmx"):
        super().__init__(game)

        self.next_level = None

        self.physspace = pymunk.Space()
        self.physspace.gravity = 0, 0

        self.button_bag = create_button_bag()

        button_bg_base = pygame.image.load("assets/textures/ButtonBG.png")
        self.button_bg = pygame.transform.scale(button_bg_base, np.array(button_bg_base.get_size()) * 3)

        conveyor_bg_base = pygame.image.load("assets/textures/ConveyorBG.png")
        self.conveyor_bg = pygame.transform.scale(conveyor_bg_base, np.array(conveyor_bg_base.get_size()) * 3)

        self.world: pyscroll.BufferedRenderer = None
        self.load_map(map_name)

        self.level_time = 0
        self.next_level_timer = 5

        self.sprite_timer = 0
        self.last_input = 0

        self.signal_radius = 0
        self.signal_source = None

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
        self.astronaut_renderer = EntityRenderer(img_astronaut, physbody=self.astronaut)
        self.astronaut_renderer.add(self.worldgroup)
        self.astronaut_state = {"has_sat": False}

        self.astronaut_sprite_normal = img_astronaut
        self.astronaut_sprite_tf = img_astronaut_tf
        self.astronaut_sprite_tr = img_astronaut_tr
        self.astronaut_sprite_tb = img_astronaut_tb
        self.astronaut_sprite_tl = img_astronaut_tl

        # Add physics from map tiles
        layer = "Collision"
        tile_size_x, tile_size_y = self.map_data.tile_size
        blocks = []
        for x, y, _ in self.map.layernames[layer].tiles():
            #props: typing.Dict = self.map.get_tile_properties(x, y, layer)
            #if "blocked" in props.keys():
            #    if props["blocked"]:
            block_body = pymunk.Body(body_type=pymunk.Body.STATIC)
            bb = pymunk.BB(x * tile_size_x,  # l
                           (y + 1) * tile_size_y,  # b
                           (x + 1) * tile_size_x,  # r
                           y * tile_size_y)  # t
            block = pymunk.Poly.create_box(block_body, (tile_size_x, tile_size_y))
            block.friction = 0.5

            blocks.append(block_body)
            block_body.position = bb.center()
            blocks.append(block)
        self.physspace.add(*blocks)

        def collision(arbiter: pymunk.Arbiter, space, data):
            if arbiter.total_ke > 100000:
                if not mixer_bump_channel.get_busy():
                    mixer_bump_channel.play(snd_bump_hard)
            elif arbiter.total_ke > 20000:
                if not mixer_bump_channel.get_busy():
                    mixer_bump_channel.play(snd_bump_light)

        handler = self.physspace.add_collision_handler(collision_types["astronaut"], collision_types["object"])
        handler.post_solve = collision

        self.win_trigger = pymunk.BB(10,10,200,200)
        self.level_won = False

        self.active_button_queue = []
        self.waiting_button_queue = []
        self.ui_group = pygame.sprite.Group()
        self.ordered_button_group = pygame.sprite.OrderedUpdates()
        for i in range(4):
            bt = ControlButton(self,next(self.button_bag),self.get_button_x(i))
            bt.countdown_dt = countdown_intervals[i]*2
            self.active_button_queue.append(bt)
            self.ordered_button_group.add(bt)

        self.spawn_next_button()
        self.spawn_next_button()
        self.spawn_next_button()
        self.align_ui_buttons()

    def load_map(self, map_id):
        self.map = load_pygame("assets/maps/" + map_id)
        self.map_data = pyscroll.TiledMapData(self.map)
        self.world = pyscroll.BufferedRenderer(self.map_data, self.get_screen_size())
        self.world.zoom = 2
        self.world.scroll((0, 300))

        self.worldgroup = pyscroll.PyscrollGroup(map_layer=self.world)

    def update(self, dt):
        super().update(dt)
        self.physspace.step(dt)
        self.worldgroup.update(dt)
        self.ui_group.update(dt)
        self.ordered_button_group.update(dt)

        self.level_time += dt

        self.signal_source = self.get_signal_position()
        if self.signal_source is not None:
            self.signal_radius += 1000*dt
            if self.signal_radius > 5000:
                self.signal_radius = 0

        # self.world.scroll((0, 1))
        self.world.center(self.astronaut.position)

        # Set correct sprite
        self.sprite_timer += dt

        self.astronaut_renderer.src_image = self.get_current_astronaut_image()

        for i in range(len(self.active_button_queue)):
            bt = self.active_button_queue[i]
            if bt.expired:
                display_debug_message('Button expired!')
                self.on_control_button_pressed(i)
                self.set_screen_shake(duration_dt=2, magnitude=2)

        if self.check_win_condition() and not self.level_won:
            self.level_won = True
            self.level_win()

        if self.level_won:
            self.next_level_timer -= dt

            if self.next_level_timer <= 0 and self.next_level is not None:
                self.game.next_screen = self.next_level(game)

        if self.check_out_of_bounds():
            self.game.next_screen = GameOverScreen(self.game, self.astronaut_state["has_sat"], self.__class__)

    def level_win(self):
        display_debug_message("A winner is you!")
        t = TextSprite("MISSION ACCOMPLISHED", ui_font_128, self.ui_group)
        t.set_sprite_position(self.get_screen_size()[0]//2, self.get_screen_size()[1]//2, center=True)

        for bt in self.active_button_queue:
            if bt is not None:
                bt.active = False
                bt.update_sprite()

    def check_out_of_bounds(self):
        grace = 100
        return (self.astronaut.position.x > self.map.width*self.map.tilewidth + grace
                or self.astronaut.position.x < 0 - grace
                or self.astronaut.position.y > self.map.height*self.map.tileheight + grace
                or self.astronaut.position.y < 0 - grace)

    def render(self, surface):
        self.worldgroup.draw(surface)

        # draw signal
        if self.signal_source is not None:
            pygame.draw.circle(surface, (0,180,0), self.world.translate_point(self.signal_source), self.signal_radius, width=2)

    def on_mouse_release(self,event):
        if any(pygame.mouse.get_pressed()):
            mx, my = pygame.mouse.get_pos()
            for i in range(len(self.active_button_queue)):
                bt = self.active_button_queue[i]
                if bt is not None:
                    if bt.is_mouse_inside(mx,my):
                        self.on_control_button_pressed(i)

    def on_resize(self):
        size = display.get_surface().get_size()
        view_center = self.world.view_rect.center
        self.world.set_size(size)
        self.world.center(view_center)
        self.align_ui_buttons()

    def on_key_escape(self, event):
        super().on_key_escape(event)
        self.game.to_main_menu()

    def on_key_press(self, event):
        if debug_mode:
            if event.key == pygame.K_DOWN:
                self.astronaut_backward()
            if event.key == pygame.K_UP:
                self.astronaut_forward()
            if event.key == pygame.K_LEFT:
                self.astronaut_turn_backward()
            if event.key == pygame.K_RIGHT:
                self.astronaut_turn_forward()

        #Num keys 1-4: 49-51
        print('Key event: '+str(event.key))
        if event.key == 49 or event.key == 113:
            self.on_control_button_pressed(0)
        if event.key == 50 or event.key == 119:
            self.on_control_button_pressed(1)
        if event.key == 51 or event.key == 101:
            self.on_control_button_pressed(2)
        if event.key == 52 or event.key == 114:
            self.on_control_button_pressed(3)

    def on_control_button_pressed(self,index):
        bt = self.active_button_queue[index]
        if bt is None or not bt.active:
            display_debug_message('This action is not ready yet')
            #TODO: Display message
            return

        mag = bt.magnitude
        if bt.type==3:
            self.astronaut_backward(mag)
        if bt.type==0:
            self.astronaut_forward(mag)
        if bt.type==1:
            self.astronaut_turn_backward(mag)
        if bt.type==2:
            self.astronaut_turn_forward(mag)
        self.set_screen_shake(1,5)

        interpolator = interpolation.Smooth()
        bt.animate(Animation2D((0,0),(200,200),2,interpolation=interpolator))

        bt.on_execute()
        #bt.stop_animations()
        #self.active_button_queue[index] = None
        self.ordered_button_group.remove(bt)

        next_bt = self.waiting_button_queue.pop(0)
        distance_x= self.get_button_x(index) - next_bt.get_sprite_position_x()
        next_bt.stop_animations()
        next_bt.animate(Animation2D((0,0),(distance_x,0),.5,interpolation=interpolator))
        next_bt.countdown_dt = countdown_intervals[index]
        self.active_button_queue[index] = next_bt

        new_bt = self.spawn_next_button()
        next_bt.update(0)
        #self.align_ui_buttons()
        for i in range(len(self.waiting_button_queue)):
            bt = self.waiting_button_queue[i]
            current_x = bt.get_sprite_position_x()
            target_x = self.get_button_x(i+4)
            distance_x= target_x - current_x
            bt.stop_animations()
            bt.animate(Animation2D((0,0),(distance_x,0),.5))


    def get_current_astronaut_image(self):
        if self.sprite_timer > 0.5:
            return self.astronaut_sprite_normal
        else:
            if self.last_input == 1:
                return self.astronaut_sprite_tf
            elif self.last_input == 2:
                return self.astronaut_sprite_tb
            elif self.last_input == 3:
                return self.astronaut_sprite_tr
            elif self.last_input == 4:
                return self.astronaut_sprite_tl
            else:
                return self.astronaut_sprite_normal

    def astronaut_forward(self, magnitude=1):
        self.astronaut.apply_impulse_at_local_point((2000*magnitude,0), (0,0))
        self.last_input = 1
        self.sprite_timer = 0
        snd_jet1.play()

    def astronaut_backward(self, magnitude=1):
        self.astronaut.apply_impulse_at_local_point((-2000*magnitude,0), (0,0))
        self.last_input = 2
        self.sprite_timer = 0
        snd_jet1.play()

    def astronaut_turn_forward(self, magnitude=1):
        self.astronaut.apply_impulse_at_local_point((-200*magnitude,0), (30,60))
        self.astronaut.apply_impulse_at_local_point((200*magnitude,0), (-30,-60))
        self.last_input = 3
        self.sprite_timer = 0
        snd_jet2.play()

    def astronaut_turn_backward(self, magnitude=1):
        self.astronaut.apply_impulse_at_local_point((200*magnitude,0), (30,60))
        self.astronaut.apply_impulse_at_local_point((-200*magnitude,0), (-30,-60))
        self.last_input = 4
        self.sprite_timer = 0
        snd_jet2.play()

    def align_ui_buttons(self):
        w,h = self.get_screen_size()
        sw,sh = btn_left_img.get_size()

        i = 0
        for bt in self.active_button_queue + self.waiting_button_queue:
            if bt is None:
                i+=1
                continue

            #bt.set_sprite_position(y=0,stop_animations=False)
            bx = self.get_button_x(i)
            bt._sprite_y = h-sh-8*3
            bt.rect.y = 0
            bt._sprite_x = bx
            bt._sprite_x = bx
            i+=1

    def spawn_next_button(self):
        try:
            bt_type = next(self.button_bag)
        except StopIteration:
            self.button_bag = create_button_bag()
            bt_type = next(self.button_bag)
        w,h = self.get_screen_size()
        x = w+100
        bt = ControlButton(self,bt_type,x,1,active=False)
        self.waiting_button_queue.append(bt)

        self.reverse_ordered_button_queue()
        self.ordered_button_group.add(bt)
        self.reverse_ordered_button_queue()

        return bt

    def reverse_ordered_button_queue(self):
        nl = []
        for bt in self.ordered_button_group:
            nl.append(bt)
        nl.reverse()
        self.ordered_button_group.empty()
        for nl in nl:
            self.ordered_button_group.add(nl)


    def check_win_condition(self):
        return self.win_trigger.contains_vect(self.astronaut.position)

    def render_ui(self, screen):
        w, h = self.get_screen_size()
        bw, bh = btn_right_img.get_size()

        # Drawing debug target
        #pygame.draw.line(screen,(255,255,255),(0,h/2),(w,h/2))
        #pygame.draw.line(screen,(255,255,255),(w/2,0),(w/2,h))

        # Drawing conveyor
        conveyor_count = int(((w/2)/16*3)) + 1
        for i in range(conveyor_count):
            conv_mod = i*16*3
            screen.blit(self.conveyor_bg,(w/2+128*3+conv_mod,h-62*3-6))

        #self.button_group.draw(screen)
        self.ordered_button_group.draw(screen)

        # Drawing Progressbars
        for i in range(4):
            bx = self.get_button_x(i)
            progressbar_x = bx + 35
            progressbar_w = 36*3
            pygame.draw.rect(screen,black,(progressbar_x,h-bh-60,progressbar_w,36))

            bt = self.active_button_queue[i]
            p = 0.0
            if bt is not None:
                p = float(bt.get_countdown_progress())
            pygame.draw.rect(screen,(255,0,0),(progressbar_x,h-bh-60,int(progressbar_w*p),36))


        # Drawing conveyor background
        screen.blit(self.button_bg,(w/2-128*3, h-72*3))

        # Drawing hotkeys
        for i in range(4):
            bx = self.get_button_x(i)
            hotkey_text = ui_font_24.render(str(i + 1), False, (0, 0, 0))
            screen.blit(hotkey_text,(bx+5,h-bh-65))

        self.ui_group.draw(screen)

    def get_button_x(self, index):
        w, h = self.get_screen_size()
        bw, bh = btn_right_img.get_size()
        button_offset = 9
        bw = bw + button_offset*2

        conveyor_adjustment = 0
        if index >3:
            conveyor_adjustment = 27*3

        return (w / 2) - (bw*2) + (button_offset) + (bw * index) +conveyor_adjustment

    def get_button_ui_width(self):
        return self.get_button_x(1)-self.get_button_x(0)

    def on_screen_exit(self):
        display_debug_message('Leaving game screen.')


## PHYSICS BODY CREATORS

def create_asteroid_body(group, position=(0,0), velocity=(0,0), angular_velocity=0.1):
    asteroid = pymunk.Body()
    asteroid.position = position
    c = pymunk.Circle(asteroid, 27)
    c.density = 0.08
    c.friction = 0.4
    asteroid.angular_velocity = angular_velocity
    asteroid.velocity = velocity
    EntityRenderer(pygame.image.load("assets/textures/meteor.png"), physbody=asteroid).add(group)
    return asteroid, c


def create_clutter_body(group, clutter_type="beer", position=(0,0), rotation=0.0, velocity=(0,0), angular_velocity=0.1):
    clutter = pymunk.Body()
    clutter.position = position
    if clutter_type == "beer":
        img = pygame.image.load("assets/textures/beer.png")
    elif clutter_type == "wrench":
        img = pygame.image.load("assets/textures/wrench.png")
    elif clutter_type == "platine":
        img = pygame.image.load("assets/textures/platine.png")
    elif clutter_type == "can":
        img = pygame.image.load("assets/textures/can.png")
    elif clutter_type == "cat":
        img = pygame.image.load("assets/textures/spacecat.png")
    c = pymunk.Poly.create_box(clutter, (img.get_width(), img.get_height()))
    c.density = 0.001
    c.friction = 0.4
    clutter.angular_velocity = angular_velocity
    clutter.angle = rotation
    clutter.velocity = velocity
    EntityRenderer(img, physbody=clutter).add(group)
    return clutter, c

def create_satellite_body(group, position=(0,0), velocity=(0,0), angular_velocity=-0.1):
    satellite = pymunk.Body()
    satellite.position = position
    c = poly = pymunk.Poly(satellite, [
            (0  - 32, 11 - 32),
            (11 - 32, 0  - 32),
            (43 - 32, 21 - 32),
            (64 - 32, 53 - 32),
            (53 - 32, 64 - 32),
            (21 - 32, 43 - 32),
        ])
    c.density = 0.05
    c.friction = 0.4
    c.collision_type = collision_types["collectible"]
    satellite.angular_velocity = angular_velocity
    satellite.velocity = velocity
    EntityRenderer(pygame.image.load("assets/textures/satellite.png"), physbody=satellite).add(group)
    return satellite, c


class Level1(BaseLevel):
    def __init__(self, game):
        super().__init__(game, map_name="level1.tmx")

        self.next_level = Level2

        self.astronaut.position = (13*32, 15.5*32)
        self.astronaut_state["has_sat"] = False

        self.satellite, c = create_satellite_body(self.worldgroup, position=(27 * 32, 17 * 32))
        self.physspace.add(self.satellite, c)
        self.physspace.add(create_asteroid_body(self.worldgroup, position=(26*32,7*32), velocity=(-1.,0.1)))

        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16*32,16*32), velocity=(.3,.1), rotation=-0.7, angular_velocity=0.7))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16.8*32,16.2*32), velocity=(.1,-.1), rotation=1.5, angular_velocity=-0.2))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(15.7*32,16.5*32), velocity=(.05,.1), rotation=2.3, angular_velocity=-0.1))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16.1*32,18.*32), velocity=(0,-.1), rotation=0.5, angular_velocity=-0.1))
        self.physspace.add(create_clutter_body(self.worldgroup, "wrench", position=(14.9*32,14*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "can", position=(23.5*32,14.2*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "platine", position=(15.8*32,9.8*32), velocity=(0,0), angular_velocity=0))
        self.physspace.add(create_clutter_body(self.worldgroup, "cat", position=(27*32,12*32), velocity=(-0.7, 0.1), angular_velocity=0.0))
        self.win_trigger = pymunk.BB(10*32,12*32,16*32,18*32)

        def collect(arbiter, space, data):
            collectible = arbiter.shapes[1]
            space.remove(collectible, collectible.body)
            associated_sprites = filter(lambda s: collectible in s.physbody.shapes, self.worldgroup.sprites())
            self.worldgroup.remove(*associated_sprites)
            self.astronaut_state["has_sat"] = True
            print(self.astronaut_state)

            self.astronaut_sprite_normal = img_astronaut_sat
            self.astronaut_sprite_tf = img_astronaut_tf_sat
            self.astronaut_sprite_tr = img_astronaut_tr_sat
            self.astronaut_sprite_tb = img_astronaut_tb_sat
            self.astronaut_sprite_tl = img_astronaut_tl_sat
            return False

        handler = self.physspace.add_collision_handler(collision_types["astronaut"], collision_types["collectible"])
        handler.pre_solve = collect

    def check_win_condition(self):
        return super().check_win_condition() and self.astronaut_state["has_sat"]

    def get_signal_position(self):
        return self.satellite.position if not self.astronaut_state["has_sat"] else None


class Level2(BaseLevel):
    def __init__(self, game):
        super().__init__(game, map_name="level2.tmx")

        self.astronaut.position = (13*32, 14.5*32)
        self.astronaut.angle = 0.15
        self.astronaut_state["has_sat"] = False

        self.next_level = Level3

        self.satellite, c = create_satellite_body(self.worldgroup, position=(25.8*32,24*32))
        self.physspace.add(self.satellite, c)
        self.physspace.add(create_asteroid_body(self.worldgroup, position=(26*32,7*32), velocity=(-1.,0.1)))

        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(22*32,16*32), velocity=(.3,.1), rotation=-0.7, angular_velocity=0.7))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(23.8*32,16.2*32), velocity=(.1,-.1), rotation=1.5, angular_velocity=-0.2))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(19.7*32,17.5*32), velocity=(.05,.1), rotation=2.3, angular_velocity=-0.1))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16.1*32,18.*32), velocity=(0,-.1), rotation=0.5, angular_velocity=-0.1))
        self.physspace.add(create_clutter_body(self.worldgroup, "wrench", position=(25.9*32,19*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "can", position=(23.5*32,14.2*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "platine", position=(15.8*32,9.8*32), velocity=(0,0), angular_velocity=0))
        self.physspace.add(create_clutter_body(self.worldgroup, "cat", position=(29*32,21*32), velocity=(-0.7, 0.1), angular_velocity=0.0))
        self.win_trigger = pymunk.BB(10*32,12*32,16*32,18*32)

        def collect(arbiter, space, data):
            collectible = arbiter.shapes[1]
            space.remove(collectible, collectible.body)
            associated_sprites = filter(lambda s: collectible in s.physbody.shapes, self.worldgroup.sprites())
            self.worldgroup.remove(*associated_sprites)
            self.astronaut_state["has_sat"] = True
            print(self.astronaut_state)

            self.astronaut_sprite_normal = img_astronaut_sat
            self.astronaut_sprite_tf = img_astronaut_tf_sat
            self.astronaut_sprite_tr = img_astronaut_tr_sat
            self.astronaut_sprite_tb = img_astronaut_tb_sat
            self.astronaut_sprite_tl = img_astronaut_tl_sat
            return False

        handler = self.physspace.add_collision_handler(collision_types["astronaut"], collision_types["collectible"])
        handler.pre_solve = collect

    def check_win_condition(self):
        return super().check_win_condition() and self.astronaut_state["has_sat"]

    def get_signal_position(self):
        return self.satellite.position if not self.astronaut_state["has_sat"] else None

class Level3(BaseLevel):
    def __init__(self, game):
        super().__init__(game, map_name="level3.tmx")

        self.next_level = None

        self.astronaut.position = (13*32, 14*32)
        self.astronaut_state["has_sat"] = False

        self.satellite, c = create_satellite_body(self.worldgroup, position=(24*32,9*32))
        self.physspace.add(self.satellite, c)
        self.physspace.add(create_asteroid_body(self.worldgroup, position=(19*32,14*32)))

        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16*32,16*32), velocity=(.3,.1), angular_velocity=0.7))
        self.physspace.add(create_clutter_body(self.worldgroup, "beer", position=(16.8*32,16.2*32), velocity=(.1,-.1), angular_velocity=-0.2))
        self.physspace.add(create_clutter_body(self.worldgroup, "wrench", position=(15*32,14*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "can", position=(19.5*32,17.2*32)))
        self.physspace.add(create_clutter_body(self.worldgroup, "cat", position=(26*32,12*32), velocity=(-0.7, 0.1), angular_velocity=0.2))


        self.win_trigger = pymunk.BB(10*32,12*32,16*32,18*32)

        def collect(arbiter, space, data):
            collectible = arbiter.shapes[1]
            space.remove(collectible, collectible.body)
            associated_sprites = filter(lambda s: collectible in s.physbody.shapes, self.worldgroup.sprites())
            self.worldgroup.remove(*associated_sprites)
            self.astronaut_state["has_sat"] = True
            print(self.astronaut_state)

            self.astronaut_sprite_normal = img_astronaut_sat
            self.astronaut_sprite_tf = img_astronaut_tf_sat
            self.astronaut_sprite_tr = img_astronaut_tr_sat
            self.astronaut_sprite_tb = img_astronaut_tb_sat
            self.astronaut_sprite_tl = img_astronaut_tl_sat
            return False

        handler = self.physspace.add_collision_handler(collision_types["astronaut"], collision_types["collectible"])
        handler.pre_solve = collect

    def check_win_condition(self):
        return super().check_win_condition() and self.astronaut_state["has_sat"]

    def get_signal_position(self):
        return self.satellite.position if not self.astronaut_state["has_sat"] else None

class GameOverScreen(Screen):
    def __init__(self, game, has_sat=False, reset_level:typing.ClassVar[BaseLevel]=Level1):
        super().__init__(game)

        self.game = game
        self.screen = game.screen
        self.reset_level = reset_level
        self.group = pygame.sprite.Group()
        self.ui_group = pygame.sprite.Group()
        self.bg_image = pygame.transform.smoothscale(black_hole_bg, self.get_screen_size())

        self.astronaut = pygame.sprite.Sprite(self.group)
        self.astronaut_img: pygame.Surface = img_astronaut_sat if has_sat else img_astronaut
        self.astronaut.image = self.astronaut_img
        self.astronaut.rect = self.astronaut_img.get_rect()

        self.astronaut_scale = 2
        self.astronaut_rot = 0

        self.quote_alpha = -0.8
        self.quote = TextSprite(["“Lost, so small amid that dark,",
                                 "hands grown cold, body image fading down corridors",
                                 "of television sky.” - William Gibson"])
        self.ui_group.add(self.quote)


    def update(self, dt):
        super().update(dt)
        self.group.update(dt)
        self.ui_group.update(dt)

        self.astronaut_scale -= 0.25*dt
        self.astronaut_rot += 160*dt

        if self.astronaut_scale <= 0.1:
            self.group.remove(self.astronaut)

        self.quote.rect.center = (self.get_screen_size()[0]//2, self.get_screen_size()[1]//2+300)
        self.quote_alpha += 0.3*dt
        self.quote.image.set_alpha(0)
        self.quote.image.set_alpha(int(255*max(0., min(1., self.quote_alpha))))

    def render(self, surface):
        surface.blit(self.bg_image, (0,0))

        if self.astronaut_scale > 0.1:
            self.astronaut.image = pygame.transform.rotate(pygame.transform.scale(self.astronaut_img,
                                                                                  (int(self.astronaut_img.get_width() * self.astronaut_scale*self.astronaut_scale),
                                                                                   int(self.astronaut_img.get_height() * self.astronaut_scale*self.astronaut_scale))), int(self.astronaut_rot))
            self.astronaut.rect = self.astronaut.image.get_rect()
            self.astronaut.rect.center = (self.get_screen_size()[0]//2, self.get_screen_size()[1]//2)
        self.group.draw(surface)

    def on_resize(self):
        size = display.get_surface().get_size()
        self.bg_image = pygame.transform.smoothscale(black_hole_bg, self.get_screen_size())

    def on_key_release(self, event):
        if self.quote_alpha > 0:
            game.next_screen = self.reset_level(self.game)

    def get_screen_size(self):
        return self.game.screen.get_size()

    def render_ui(self, screen):
        self.ui_group.draw(screen)
        #screen.blit(self.quote.image, (0,0))

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
        self.ticks = duration
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
        self._layer = 4

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


    def set_sprite_position(self, x=None, y=None, center=False, stop_animations=True):
        if x is not None:
            if center:
                self._sprite_x = x-self.rect.width//2
            else:
                self._sprite_x = x
        if y is not None:
            if center:
                self._sprite_y = y-self.rect.height//2
            else:
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

    def __init__(self, level, type:int, x, magnitude = 1,active:bool=True,countdown_dt=3):
        super().__init__()
        self.level=level
        self.type = type
        self.magnitude =magnitude
        self.active = active
        self.expired = False

        w,h = level.get_screen_size()

        self.countdown_dt=countdown_dt
        self.countdown_current=0

        self.update_sprite()
        self.rect: pygame.Rect = self.image.get_rect()

        sw,sh = self.image.get_size()
        self._sprite_x = x
        self._sprite_y = h-sh-8*3
        self.rect.x = self._sprite_x
        self.rect.y = self._sprite_y

    def update_sprite(self):
        if self.active:
            if self.type==0:
                self.image=btn_decelerate_img
            if self.type==1:
                self.image=btn_left_img
            if self.type==2:
                self.image=btn_right_img
            if self.type==3:
                self.image=btn_accelerate_img
        else:
            if self.type==0:
                self.image=btn_decelerate_img_disabled
            if self.type==1:
                self.image=btn_left_img_disabled
            if self.type==2:
                self.image=btn_right_img_disabled
            if self.type==3:
                self.image=btn_accelerate_img_disabled

    def on_execute(self):
        pass

    def update(self, dt):
        super().update(dt)

        if self.active and self.level.level_won is not True:
            self.countdown_current += dt

        if self.countdown_current >= self.countdown_dt:
            self.expired = True

    def get_countdown_progress(self):
        return float(self.countdown_current) / float(self.countdown_dt)

    def animate(self, animation: Animation2D):
        super().animate(animation)

        def finished():
            if self in self.level.active_button_queue:
                self.active = True
                self.update_sprite()

        animation.add_animation_finished_callback(finished)

    def is_mouse_inside(self,mx,my):
        return self.rect.collidepoint(mx,my)

class TextSprite(AnimatedEntity):
    def __init__(self, text, font=ui_font_48, *groups):
        super().__init__(*groups)

        if isinstance(text, list):
            linesurfs = []
            for line in text:
                textsurface = font.render(line, True, (230, 230, 230)).convert_alpha()
                w = textsurface.get_width() + 2
                h = textsurface.get_height() + 2
                image = pygame.Surface((w,h)).convert_alpha()
                image.fill((0, 0, 0, 0))
                image.blit(font.render(line, True, (0, 0, 0)).convert_alpha(), (2, 2))
                image.blit(textsurface, (0, 0))
                linesurfs.append(image)
            self.image = pygame.Surface((max(map(lambda i: i.get_width(), linesurfs)),
                                        #sum(map(lambda i: i.get_height(), linesurfs)))
                                         font.get_height()*len(text))
                                        ).convert_alpha()
            self.image.fill((0, 0, 0, 0))
            for i, line in enumerate(linesurfs):
                self.image.blit(line,
                                (int(self.image.get_width()/2-line.get_width()/2),
                                font.get_height()*i))
            self.image = self.image
            self.rect = self.image.get_rect()
        else:
            textsurface = font.render(text, True, (230, 230, 230)).convert_alpha()
            w = textsurface.get_width() + 2
            h = textsurface.get_height() + 2
            self.image = pygame.Surface((w,h)).convert_alpha()
            self.image.fill((0, 0, 0, 0))
            self.image.blit(font.render(text, True, (0, 0, 0)).convert_alpha(),(2,2))
            self.image.blit(textsurface, (0,0))
            self.rect = self.image.get_rect()


### DEBUG MESSAGES
_debug_message_list = []
debug_message_default_time = 5


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

    game.current_screen = MainMenuScreen(game)
    game.current_screen.on_screen_enter()
    game.current_screen.on_game_startup()

    print("Starting Game Loop")
    game.game_loop()
    print('Game closed. Goodbye.')


if __name__ == '__main__':
    main()
