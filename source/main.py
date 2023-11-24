import os

import dearpygui.dearpygui as dpg

import themes
from LuaNodes import *
import pyperclip as pc
import json

dpg.create_context()
dpg.configure_app(manual_callback_management=True)
dpg.create_viewport(title='Lua Node Editor', width=1200, height=800)


# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # check for no other link to have the same end
    for l in globals.links:
        if l.to_attribute == app_data[1]:
            return

    id = dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    from_node = dpg.get_item_parent(app_data[0])
    to_node = dpg.get_item_parent(app_data[1])

    globals.links += [Link(id, from_node, to_node, app_data[0], app_data[1])]


# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)
    globals.links = list(filter(lambda l: l.id != app_data, globals.links))


def get_mouse_pos_relative_to(item):
    item_min_rect = dpg.get_item_state(item)["rect_min"]
    mouse_pos = dpg.get_mouse_pos(local=False)

    return [mouse_pos[0] - item_min_rect[0], mouse_pos[1] - item_min_rect[1]]


def get_mouse_pos_in_node_editor():
    ref_node_rect_min = dpg.get_item_state("reference_node")["rect_min"]

    node_editor_rect_min = dpg.get_item_state("node_editor_container")["rect_min"]
    ref_node_rect_min = [ref_node_rect_min[0] - node_editor_rect_min[0], ref_node_rect_min[1] - node_editor_rect_min[1]]

    local_mouse_pos = get_mouse_pos_relative_to("node_editor_container")
    return [local_mouse_pos[0] - ref_node_rect_min[0], local_mouse_pos[1] - ref_node_rect_min[1]]


def get_starting_node():
    for node in globals.nodes:
        if isinstance(node, LuaStartNode):
            return node
    return None


def show_modal(window_title, modal_message, ok_callback=None, show_cancel=False, cancel_callback=None):
    dpg.configure_item("modal", label=window_title)
    dpg.configure_item("modal_text", default_value=modal_message)
    dpg.configure_item("modal", show=True)
    dpg.configure_item("modal", pos=[dpg.get_viewport_width() // 2 - 150, dpg.get_viewport_height() // 2 - 100])

    dpg.configure_item("modal_cancel", show=show_cancel)
    dpg.configure_item("modal_ok", callback=default_modal_callback if ok_callback is None else ok_callback)
    if show_cancel:
        dpg.configure_item("modal_cancel", callback=cancel_callback)


def generate_code():
    code = ""
    # add variable declaration code
    for node in globals.nodes:
        if isinstance(node, LuaVariableNode) or isinstance(node, LuaTable):
        # if isinstance(node, LuaVariableNode):
            if not node.has_from_node():
                code += node.generate_code()

    # add global functions code
    for node in globals.nodes:
        if isinstance(node, LuaNodeFunction):
            if not node.has_from_node() and not node.is_inline():
                code += node.generate_code()

    start_node = get_starting_node()
    if start_node is None:
        show_modal("Warning", "Start node not found! Please add one.")
    else:
        code += start_node.generate_code()

    dpg.configure_item("generated_code", default_value=code)


def delete_selected_nodes():
    selected_nodes = dpg.get_selected_nodes("node_editor")
    globals.nodes = list(filter(lambda n: n.id not in selected_nodes, globals.nodes))

    # ref_node = dpg.get_item_label(node)
    for node in selected_nodes:
        if dpg.get_item_label(node) == dpg.get_item_label("reference_node"):
            continue
        dpg.delete_item(node)
        # dpg.delete_item(node)

    # delete links that are left hanging
    node_ids = [node.id for node in globals.nodes]
    globals.links = list(filter(lambda l: l.from_node in node_ids and l.to_node in node_ids, globals.links))


def create_node(node_type):
    node: LuaNode = create_node_of_type(node_type)

    if node:
        node.submit("node_editor")
        dpg.configure_item(node.id, pos=get_mouse_pos_in_node_editor())
        globals.nodes.append(node)
        themes.apply_theme(node)

    dpg.configure_item("menu_create_node", show=False)


def right_click_callback(sender, app_data, user_data):
    if dpg.is_item_hovered("node_editor"):
        dpg.configure_item("menu_create_node", show=True, pos=dpg.get_mouse_pos(local=False))
        dpg.focus_item("menu_input_create_node")
        dpg.set_value("menu_input_create_node", "")
        dpg.set_value("node_search_filter", "")


def key_press_callback(s, key):
    if key == dpg.mvKey_Delete:
        delete_selected_nodes()
    elif key == dpg.mvKey_T:
        for node in globals.nodes:
            if isinstance(node, LuaVariableNode):
                dpg.configure_item(node.attribute_var.value, multiline=True)

        pass
        print(globals.nodes)
        print(globals.links)
        for child in dpg.get_item_children("node_search_filter", slot=1):
            print(dpg.get_item_state(child))
    elif dpg.is_key_down(dpg.mvKey_Control):
        if key == dpg.mvKey_1:
            dpg.show_item_registry()
        if key == dpg.mvKey_2:
            dpg.show_style_editor()
        elif key == dpg.mvKey_S:
            # create save folder if it doesnt exist
            create_folder_if_not_exists("save_files")
            dpg.show_item("save_dialog")
        elif key == dpg.mvKey_L:
            create_folder_if_not_exists("save_files")
            dpg.show_item("load_dialog")


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            print(f"Error creating folder '{folder_path}': {e}")
    else:
        print(f"Folder '{folder_path}' already exists.")


def is_editor_empty():
    return globals.links == [] and globals.nodes == []


def menu_pressed_new_file():
    # already empty, do nothing
    if is_editor_empty():
        return

    def clear_editor_and_hide_modal():
        reset_node_editor()
        default_modal_callback()

    show_modal("You are trying to create a new board", "All nodes will be erased. Continue?",
               ok_callback=clear_editor_and_hide_modal, show_cancel=True, cancel_callback=default_modal_callback)


def reset_node_editor():
    globals.nodes = []
    globals.links = []
    children = dpg.get_item_children("node_editor", slot=1)
    for child in children:
        # avoid deleting the reference node
        if dpg.get_item_label(child) == dpg.get_item_label("reference_node"):
            continue
        # delete twice cuz it doesnt work otherwise
        dpg.delete_item(child)


def save(file_path):
    with open(file_path, 'w') as save_file:
        json_obj = {
            "nodes": {},
            "links": {}
        }

        nod: LuaNode
        for node in globals.nodes:
            json_obj["nodes"][node.id] = node.serialize()
        link: Link
        for link in globals.links:
            json_obj["links"][link.id] = link.serialize()

        json_string = json.dumps(json_obj, indent=2)
        save_file.write(json_string)


def load(file_path):
    # try:
    with open(file_path, 'r') as file:
        # Do something with the file, e.g., read its content
        json_string = file.read()

        data = json.loads(json_string)
        # after conversion to object was successful, reset node editor in order to populate again
        reset_node_editor()

        new_node_data = {}
        for node_id, node_data in data["nodes"].items():
            # try:
            new_node: LuaNode = create_node_of_type(node_data["node_type"])
            new_node.submit("node_editor")

            new_node.deserialize(node_data)
            new_node_data[node_id] = {
                "new_id": new_node.id,
                "new_attributes": dict(
                    zip(list(node_data["attributes"].keys()), [attr.id for attr in new_node.node_attributes]))
            }
            globals.nodes.append(new_node)
            themes.apply_theme(new_node)

            # except:
            #     pass

        for link_id, link_data in data["links"].items():
            # try:
            from_node = new_node_data[str(link_data["from_node"])]["new_id"]
            to_node = new_node_data[str(link_data["to_node"])]["new_id"]
            from_attribute = new_node_data[str(link_data["from_node"])]["new_attributes"][
                str(link_data["from_attribute"])]
            to_attribute = new_node_data[str(link_data["to_node"])]["new_attributes"][str(link_data["to_attribute"])]

            new_link_id = dpg.add_node_link(from_attribute, to_attribute, parent="node_editor")
            new_link = Link(new_link_id, from_node, to_node, from_attribute, to_attribute)

            globals.links.append(new_link)
            # except:
            #     pass

        dpg.clear_selected_nodes("node_editor")
        dpg.clear_selected_links("node_editor")

    # except:
    #     dpg.split_frame(delay=1)
    #     show_modal("Error", "Something went wrong!")


with dpg.handler_registry():
    dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=right_click_callback)
    dpg.add_key_press_handler(callback=key_press_callback)

with dpg.theme() as reference_node_theme:
    with dpg.theme_component(dpg.mvAll):
        # make it invisible in the node editor
        dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundHovered, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundSelected, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_NodeOutline, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_TitleBar, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_TitleBarHovered, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_TitleBarSelected, (255, 0, 0, 0), category=dpg.mvThemeCat_Nodes)

        # make it tiny in the node editor
        dpg.add_theme_style(dpg.mvNodeStyleVar_NodePadding, 1, 0, category=dpg.mvThemeCat_Nodes)

themes.init_themes()

def load_file_callback(sender, app_data):
    path = list(app_data["selections"].values())[0]
    load(path)


def save_file_callback(sender, app_data):
    path = None
    if len(app_data["selections"]) == 0:
        print(app_data)
        path = app_data["file_path_name"]
    else:
        path = list(app_data["selections"].values())[0]
    print(path)
    save(path)


def file_dialog_cancel_callback(sender, app_data):
    pass


# file selector
# load
with dpg.file_dialog(
        directory_selector=False, show=False, callback=load_file_callback, tag="load_dialog",
        cancel_callback=file_dialog_cancel_callback, width=700, height=400, modal=True, default_path="save_files"):
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".lvs", color=(0, 255, 0, 255), custom_text="[Lua Visual Save]")

# save
with dpg.file_dialog(
        directory_selector=False, show=False, callback=save_file_callback, tag="save_dialog",
        cancel_callback=file_dialog_cancel_callback, width=700, height=400, modal=True, default_path="save_files"):
    dpg.add_file_extension(".*")
    dpg.add_file_extension(".lvs", color=(0, 255, 0, 255), custom_text="[Lua Visual Save]")

# create node window popup
with dpg.window(label="Create node", show=False, tag="menu_create_node", no_title_bar=True, popup=True,
                no_move=True, max_size=(1000, 200)):
    dpg.add_input_text(hint="Search", tag="menu_input_create_node",
                       callback=lambda s, a: dpg.set_value("node_search_filter", a))
    with dpg.group(horizontal=False):
        with dpg.filter_set(tag="node_search_filter"):
            # dpg.add_text("aaa1.c", filter_key="aaa1.c", bullet=True)
            for node_type, name in lua_ntNames.items():
                dpg.add_button(label=name, filter_key=str(name), user_data=node_type,
                               callback=lambda s, a, u: create_node(u))

# main window
with dpg.window(tag="main_window") as main_win:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="New", callback=lambda: menu_pressed_new_file())
            dpg.add_menu_item(label="Save as", callback=lambda: dpg.show_item("save_dialog"))
            dpg.add_menu_item(label="Load", callback=lambda: dpg.show_item("load_dialog"))

    with dpg.group(horizontal=True):
        # with dpg.child_window(width=150):
        #     pass
        with dpg.group(tag="node_editor_container"):
            # with dpg.child_window(tag="test_tag", width=-350):
            with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, minimap=True,
                                 minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
                                 tag="node_editor", width=-350) as node_editor:
                with dpg.node(pos=(0, 0), label="", draggable=False, tag="reference_node"):
                    pass

                # with dpg.node(label="Node 2", tag="node22"):
                #     with dpg.node_attribute(label="Node A3"):
                #         dpg.add_input_float(label="F3", width=200)
                #
                #     with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                #         dpg.add_input_float(label="F4", width=200)

        with dpg.group():
            with dpg.group(horizontal=True):
                # with dpg.child_window(tag="test_tag"):
                dpg.add_button(label="Generate code", callback=generate_code)
                dpg.add_button(label="Copy code", callback=lambda: pc.copy(dpg.get_value("generated_code")))
            dpg.add_input_text(height=-1, multiline=True, tag="generated_code", width=350)


# dpg.bind_item_handler_registry("node_editor", "node_editor_handler")


def empty_func():
    pass


def default_modal_callback():
    dpg.configure_item("modal", show=False)


# modal window
with dpg.window(label="test", modal=True, no_move=True, show=False,
                pos=[dpg.get_viewport_width() // 2 - 150, dpg.get_viewport_height() // 2 - 100],
                no_resize=True, tag="modal", min_size=[0, 0]) as modal:
    dpg.add_text("", tag="modal_text")
    dpg.add_spacer()
    with dpg.group(horizontal=True):
        dpg.add_button(label="Ok", callback=default_modal_callback, tag="modal_ok")
        dpg.add_button(label="Cancel", show=False, tag="modal_cancel")

# hide reference node on first frame (actually cant do it because it wont have rect_min set properly)
# dpg.set_frame_callback(frame=1, callback=lambda: dpg.hide_item("reference_node"))
# so i just hide it instead
dpg.bind_item_theme("reference_node", reference_node_theme)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(main_win, True)
while dpg.is_dearpygui_running():
    jobs = dpg.get_callback_queue()  # retrieves and clears queue
    dpg.run_callbacks(jobs)
    dpg.render_dearpygui_frame()

# dpg.start_dearpygui()
dpg.destroy_context()
