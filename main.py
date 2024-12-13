# -*- coding: utf-8 -*-
from components.texture import Texture
from core.main_loop import MainLoop
from core.ecs import ECSManager
from systems.render_system import RenderSystem


def main():
	ecs = ECSManager()

	render_system = RenderSystem(ecs)
	player = ecs.create_entity()
	ecs.add_component(player, Texture("player.png"))
	ecs.add_system(render_system)

	main_loop = MainLoop(ecs, render_system.renderer)
	main_loop.run()


if __name__ == "__main__":
	main()
