# -*- coding:utf-8
import time
from core.time_core import TimeManager
from Context.context import global_data as GD


class MainLoop(object):
    def __init__(self, target_fps=60):
        self.target_fps = target_fps
        self.running = True

    def run(self):
        time_manager = TimeManager()

        try:
            while self.running:
                delta_time = time_manager.get_delta_time()

                systems = GD.ecs_manager.get_systems()
                for system in systems:
                    system.update(delta_time)

                self.handle_events()
                # control the frame rate
                time.sleep(max(1 / self.target_fps - (time_manager.get_delta_time()), 0))
        except KeyboardInterrupt:
            self.running = False

    def handle_events(self):
        window = GD.renderer.window
        window.poll_events()
        self.running = not window.should_close()
