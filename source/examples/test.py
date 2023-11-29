# import dearpygui.dearpygui as dpg
#
# dpg.create_context()
#
# def change_text(sender, app_data):
#     # dpg.set_value("text item", f"Mouse Button ID: {app_data}")
#     if app_data[0] == 1:
#         print(app_data)
#
#         with dpg.popup(dpg.last_item()):
#             filter = ""
#             def setFilter(sender, data):
#                 # print(sender, data)
#                 filter = data
#                 print(dpg.last_item())
#
#             dpg.add_input_text(tag="", callback=setFilter)
#             elements = ["this", "this one", "this one should not", "this one should not something"]
#
#             for el in elements:
#                 if not filter in el:
#                     continue
#                 dpg.add_text(el)
#
#
#
#
# def visible_call(sender, app_data):
#     # print("I'm visible")
#     pass
#
# with dpg.item_handler_registry(tag="widget handler") as handler:
#     dpg.add_item_clicked_handler(callback=change_text)
#     dpg.add_item_visible_handler(callback=visible_call)
#
# # with dpg.window(tag="Primary Window", width=500, height=300):
# with dpg.window(label="test", tag="Primary Window"):
#     dpg.add_text("Click me with any mouse button", tag="text item")
#     # dpg.add_text("Close window with arrow to change visible state printing to console", tag="text item 2")
#
#     popup_values = ["Bream", "Haddock", "Mackerel", "Pollock", "Tilefish"]
#
#     dpg.add_text("This is a light wrapper over a window.")
#     dpg.add_text(
#         "For more control over a modal|popup window use a normal window with the modal|popup keyword and set the item handler and mouse events manually.",
#         bullet=True)
#     dpg.add_text(
#         "By default a popup will shrink fit the items it contains.This is useful for context windows, and simple modal window popups.",
#         bullet=True)
#     dpg.add_text(
#         "When a popup is active, it inhibits interacting with windows that are behind the popup. Clicking outside the popup closes it.",
#         bullet=True)
#
#     with dpg.group(horizontal=True):
#         b = dpg.add_button(label="Right Click...")
#         t = dpg.add_text("test1")
#         t2 = dpg.add_text("test2")
#         with dpg.popup(b, tag="__demo_popup1", modal=False):
#             dpg.add_text("Aquariam")
#             dpg.add_separator()
#             def call(s, a, u):
#                 dpg.set_value(u[0], u[1])
#                 # dpg.remove_alias(u[0])
#                 dpg.delete_item(u[2])
#                 print(s, a, u)
#
#             for i in popup_values:
#                 tt = dpg.add_selectable(label=i)
#                 dpg.set_item_user_data(tt, [t, i, tt])
#                 dpg.set_item_callback(tt, call)
#
# # bind item handler registry to item
# dpg.bind_item_handler_registry("text item", "widget handler")
# # dpg.bind_item_handler_registry("text item 2", "widget handler")
#
# dpg.create_viewport(title='Custom Title', width=800, height=600)
# dpg.setup_dearpygui()
# dpg.show_viewport()
# dpg.set_primary_window("Primary Window", True)
# dpg.start_dearpygui()
# dpg.destroy_context()


import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=600)

# dpg.add_colormap_registry(label="Demo Colormap Registry", tag="__demo_colormap_registry")
colormap_reg = dpg.add_colormap_registry()

# with dpg.window(label="test"):
#     def call(sender, app_data, user_data):
#         print(sender, app_data, user_data)
#     # dpg.add_colormap([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]], False)
#     # dpg.add_colormap_button(label="butt", default_value=(255, 0, 0, 255), width=-1, height=50, callback=call)
#     x = dpg.add_colormap([[0, 0, 0, 255], [255, 255, 255, 255]], False, parent=colormap_reg, label="Demo 1")
#     dpg.add_colormap_button(label="Colormap Button 1")
#     dpg.bind_colormap(dpg.last_item(), x)

demo.show_demo()
# dpg.show_documentation()
# dpg.show_style_editor()
# dpg.show_debug()
# dpg.show_about()
# dpg.show_metrics()
# dpg.show_font_manager()
# dpg.show_item_registry()

dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
dpg.destroy_context()