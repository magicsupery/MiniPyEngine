# -*- coding:utf-8 -*-
import ctypes
import platform
from abc import ABC

import vulkan as vk
import glfw
from graphics.renderer import Renderer

if platform.system() != "Windows":
	raise Exception("This renderer only works on Windows")


class VulkanRenderer(Renderer, ABC):
	def __init__(self):
		self.in_flight_fences = None
		self.render_finished_semaphores = None
		self.image_available_semaphores = None
		self.command_buffers = None
		self.graphics_queue = None
		self.physical_device = None
		self.device = None
		self.surface = None
		self.instance = None
		self.window = None
		self.title = None
		self.height = None
		self.width = None

	def initialize(self, width, height, title):
		self.width = width
		self.height = height
		self.title = title

		if not glfw.init():
			raise Exception("GLFW initialization failed")

		glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
		self.window = glfw.create_window(width, height, title, None, None)
		self.init_vulkan()

	def init_vulkan(self):
		self.create_instance()
		self.create_surface()
		self.create_device()
		self.create_swapchain()
		self.create_image_views()
		self.create_graphics_pipeline()
		self.create_framebuffers()
		self.create_command_pool()
		self.create_command_buffers()
		self.create_sync_objects()

	def create_instance(self):
		app_info = vk.VkApplicationInfo(
			sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
			pApplicationName="Hello Triangle",
			applicationVersion=vk.VK_MAKE_VERSION(1, 0, 0),
			pEngineName="No Engine",
			engineVersion=vk.VK_MAKE_VERSION(1, 0, 0),
			apiVersion=vk.VK_API_VERSION_1_0
		)

		# glfw_extensions = glfw.get_required_instance_extensions()
		# if not glfw_extensions:
		# 	raise Exception("GLFW extensions not found")
		# 
		# print(glfw_extensions)
		# extension_array = (ctypes.c_char_p * len(glfw_extensions))(
		# 	*[extension.encode("utf-8") for extension in glfw_extensions]
		# )
		# print(extension_array)
		create_info = vk.VkInstanceCreateInfo(
			sType=vk.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
			pApplicationInfo=app_info,
			enabledLayerCount=0,
			ppEnabledLayerNames=None
		)

		self.instance = vk.vkCreateInstance(create_info, None)

	def create_surface(self):
		# 使用 ctypes 调用 GLFW 的 glfwGetWin32Window 函数以获取 HWND。
		glfw_lib = ctypes.windll.glfw3
		glfwGetWin32Window = glfw_lib.glfwGetWin32Window
		glfwGetWin32Window.argtypes = [ctypes.c_void_p]
		glfwGetWin32Window.restype = ctypes.c_void_p

		hwnd = glfwGetWin32Window(self.window)
		if not hwnd:
			raise Exception("无法获取 Win32 窗口句柄。")
		hinstance = ctypes.windll.kernel32.GetModuleHandleW(None)

		# 创建 Win32 Surface
		create_info = vk.VkWin32SurfaceCreateInfoKHR(
			sType=vk.VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
			pNext=None,
			flags=0,
			hinstance=hinstance,
			hwnd=hwnd,
		)

		surface = vk.VK_NULL_HANDLE
		result = vk(self.instance, create_info, None, ctypes.byref(surface))
		if result != vk.VK_SUCCESS:
			raise Exception("创建 Win32 表面失败。")
		self.surface = surface

	def create_device(self):
		self.physical_device = vk.vkEnumeratePhysicalDevices(self.instance)[0]

		queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self.physical_device)
		queue_family_indices = {}
		for i, queue_family in enumerate(queue_families):
			if queue_family.queueCount > 0 and queue_family.queueFlags & vk.VK_QUEUE_GRAPHICS_BIT:
				queue_family_indices["graphics"] = i
				break

		queue_priority = 1.0
		queue_create_info = vk.VkDeviceQueueCreateInfo(
			sType=vk.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
			queueFamilyIndex=queue_family_indices["graphics"],
			queueCount=1,
			pQueuePriorities=[queue_priority]
		)
		device_create_info = vk.VkDeviceCreateInfo(
			sType=vk.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
			queueCreateInfoCount=1,
			pQueueCreateInfos=[queue_create_info],
			enabledExtensionCount=0,
			ppEnabledExtensionNames=None
		)
		self.device = vk.vkCreateDevice(self.physical_device, device_create_info)
		self.graphics_queue = vk.vkGetDeviceQueue(self.device, queue_family_indices["graphics"], 0)

	def create_swapchain(self):
		pass

	def create_image_views(self):
		pass

	def create_graphics_pipeline(self):
		pass

	def create_framebuffers(self):
		pass

	def create_command_pool(self):
		pass

	def create_command_buffers(self):
		self.command_buffers = []

	def create_sync_objects(self):
		self.image_available_semaphores = vk.vkCreateSemaphore(self.device, vk.VkSemaphoreCreateInfo())
		self.render_finished_semaphores = vk.vkCreateSemaphore(self.device, vk.VkSemaphoreCreateInfo())
		self.in_flight_fences = vk.vkCreateFence(self.device,
		                                         vk.VkFenceCreateInfo(flags=vk.VK_FENCE_CREATE_SIGNALED_BIT))

	def render(self):
		pass

	def cleanup(self):
		vk.vkDestroyInstance(self.instance, None)
		glfw.destroy_window(self.window)
		glfw.terminate()
