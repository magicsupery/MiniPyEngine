# -*- coding: utf-8 -*-
import numpy as np
from components.texture import Texture
from components.transform import Transform
from components.mesh import Mesh
from core.main_loop import MainLoop
from core.ecs import ECSManager
from systems.render_system import RenderSystem


def main():
    ecs = ECSManager()

    player = ecs.create_entity()
    ecs.add_component(player, Texture("player.png"))
    ecs.add_component(player, Transform([0.0, 0.0, 0.0]))
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

    render_system = RenderSystem(ecs)
    ecs.add_system(render_system)
    main_loop = MainLoop(ecs, render_system.renderer)
    main_loop.run()


if __name__ == "__main__":
    main()
