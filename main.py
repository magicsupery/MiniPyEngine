# -*- coding: utf-8 -*-
import numpy as np

from Entity.camera import Camera
from Entity.gameobject import GameObject
from components.texture import Texture
from components.mesh import Mesh
from core.main_loop import MainLoop
from core.ecs import ECSManager
from systems.render_system import RenderSystem
from Context.context import global_data as GD


def main():
    ecs = ECSManager()
    GD.ecs_manager = ecs
    GD.ecs_manager.create_entity(Camera, position=[0.0, 0.0, 3.0])

    player = ecs.create_entity(GameObject)
    ecs.add_component(player, Texture("player.png"))
    player.Transform.position = [1.0, 0.0, 0.0]
    player.Transform.rotation = [0.0, 0.0, 0.0]
    player.Transform.scale = [1.0, 2.0, 1.0]
    vertices = np.array([
        -0.5, -0.5, 0.0,
        0.5, -0.5, 0.0,
        0.5, 0.5, 0.0
    ], dtype=np.float32)
    ecs.add_component(player, Mesh(vertices))

    # player1 = ecs.create_entity()
    # ecs.add_component(player1, Transform([0.0, 0.0, 0.0]))
    # vertices = np.array([
    #     -0.5, -0.5, 0.0,
    #     0.3, -10.0, 0.0,
    #     0.5, 0.5, 0.0
    # ], dtype=np.float32)
    # ecs.add_component(player1, Mesh(vertices))

    render_system = RenderSystem()
    ecs.add_system(render_system)
    main_loop = MainLoop()
    main_loop.run()


if __name__ == "__main__":
    main()
