import dearpygui.dearpygui as dpg
import json
from PIL import Image
import numpy as np
from WFC import WaveFunctionCollapse as wfc
from WFC import Grid, Tile

dpg.create_context()

width, height = 1920, 1080
sideData: dict = {}

def menu_loadImagesCB(sender, app_data, user_data):
    images: list[list] = []

    def file_loadImagesCB(sender, app_data, user_data):
        for path in app_data["selections"].values():
            width, height, channels, data = dpg.load_image(path)
            images.append([path, dpg.add_static_texture(parent="tex_register_main", width=width, height=height, default_value=data)])
        dpg.delete_item("file_loadImages")

        def menu_saveSidesCB(sender, app_data, user_data):
            global sideData

            dpg.delete_item("window_setSides")
            path = list(app_data["selections"].values())[0]

            with open(f"{path}.json", "w") as outfile:
                json.dump(sideData, outfile)
        
        def button_image_imageSelectCB(sender, app_data, user_data):

            def button_setCB(sender, app_data, user_data):
                global sideData

                sideData[dpg.get_value("input_text_name")] = {
                    "up": dpg.get_value("input_text_up"),
                    "down": dpg.get_value("input_text_down"),
                    "left": dpg.get_value("input_text_left"),
                    "right": dpg.get_value("input_text_right"),
                    "path": user_data[0]
                }

                dpg.delete_item("window_setImageSides")
                dpg.show_item("window_setSides")

            dpg.hide_item("window_setSides")

            with dpg.window(label="Set Sides", autosize=True, tag="window_setImageSides"):
                dpg.add_image(user_data[1], width=300, height=300)

                dpg.add_text("Name")
                dpg.add_input_text(tag="input_text_name")

                dpg.add_text("Top")
                dpg.add_input_text(tag="input_text_up")

                dpg.add_text("Bottom")
                dpg.add_input_text(tag="input_text_down")

                dpg.add_text("Left")
                dpg.add_input_text(tag="input_text_left")

                dpg.add_text("Right")
                dpg.add_input_text(tag="input_text_right")

                dpg.add_button(label="Set", callback=button_setCB, tag="button_set", user_data=user_data)

        with dpg.window(label="Set Sides", autosize=True, tag="window_setSides"):
            with dpg.menu_bar():
                dpg.add_menu_item(label="Save", callback=lambda: dpg.add_file_dialog(directory_selector=True, width=720, height=480, callback=menu_saveSidesCB), tag="menu_saveSides")
            
            dpg.delete_item("button_image")

            with dpg.child_window(width=100, height=400, tag="window_child_setSides"):
                for data in images:
                    dpg.add_image_button(texture_tag=data[1], width=50, height=50, callback=button_image_imageSelectCB, user_data=data)


    with dpg.file_dialog(directory_selector=False, callback=file_loadImagesCB, tag="file_loadImages", file_count=20, width=720, height=480):
        dpg.add_file_extension(".png")

def menu_loadDataCB(sender, app_data, user_data):

    def file_loadDataCB(sender, app_data, user_data):

        def button_rotateCB(sender, app_data, user_data):

            def button_setRotationsCB(sender, app_data, user_data):
                rawImage, PILImage, image = user_data
                for i in range(1, dpg.get_value("input_int_rotationAmount")):
                    data = np.asfarray(PILImage.rotate(-90 * i), dtype='f')
                    textureData = np.true_divide(data, 255.0)
                    rawImage = dpg.add_raw_texture(parent="tex_register_main", width=PILImage.width, height=PILImage.height, default_value=textureData, format=dpg.mvFormat_Float_rgba, tag=rawImage + "_rotate")
                    sideData[rawImage] = {
                        "up": image["left"],
                        "down": image["right"],
                        "left": image["down"],
                        "right": image["up"]
                    }
                    image = sideData[rawImage]
                    dpg.delete_item("window_rotation")
                    dpg.show_item("window_rotateSelection")

            dpg.hide_item("window_rotateSelection")

            with dpg.window(label="Rotations", autosize=True, tag="window_rotation"):
                dpg.add_image(texture_tag=user_data[0], width=50, height=50)
                dpg.add_text(label="How many rotatons?")
                dpg.add_input_int(tag="input_int_rotationAmount")
                dpg.add_button(label="Set", callback=button_setRotationsCB, user_data=user_data)
            
            dpg.delete_item(sender)
                    
        global sideData
        path = list(app_data["selections"].values())[0]
        with open(path) as f:
            sideData = json.load(f)
        dpg.delete_item("file_loadData")

        images = []
        for sides in sideData.values():
            width, height, channels, data = dpg.load_image(sides["path"])
            image = Image.open(sides["path"]).convert("RGBA")
            data = np.asfarray(image, dtype='f')
            textureData = np.true_divide(data, 255.0)
            rawImage = dpg.add_raw_texture(parent="tex_register_main", width=image.width, height=image.height, default_value=textureData, format=dpg.mvFormat_Float_rgba, tag=list(sideData.keys())[list(sideData.values()).index(sides)])
            images.append([rawImage, image, sides])
        with dpg.window(label="Select Rotatations", tag="window_rotateSelection", autosize=True):
            dpg.add_text(label="Select the tiles that need to be rotated.")
            with dpg.group(horizontal=True):
                for data in images:
                    dpg.add_image_button(data[0], label="Rotate", width=50, height=50, callback=button_rotateCB, user_data=data)

    with dpg.file_dialog(directory_selector=False, callback=file_loadDataCB, tag="file_loadData", file_count=20, width=720, height=480):
        dpg.add_file_extension(".json")

def menu_startSettingsCB(sender, app_data, user_data):
    dpg.delete_item("window_settings")
    with dpg.window(label="Settings", autosize=True, tag="window_settings"):
        dpg.add_checkbox(label="Show full process (Warning Possible Flashing Lights)", default_value=False, tag="checkbox_showAll")
        dpg.add_checkbox(label="Animate", default_value=True, tag="checkbox_animate")

def menu_startCB(sender, app_data, user_data):
    global sideData, grid, i, cell

    grid = Grid(width, height, 50, Tile.ParseTiles(sideData))
    i = 0

    def button_manualCB(sender, app_data, user_data):
        global grid, cell

        dpg.delete_item("group_manual", children_only=True)
        dpg.delete_item("rect_temp")
        collapse = wfc.ManualCollapse(cell, user_data)
        if(not collapse):
            dpg.delete_item("drawlist_main", children_only=True)
            grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
        else:
            wfc.Propagate(grid, collapse)
            dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))

        cell = wfc.Select(grid)
        dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))
        for state in cell.possibleStates:
            dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())

    def button_stepCB(sender, app_data, user_data):
        global grid, cell

        dpg.delete_item("group_manual", children_only=True)
        dpg.delete_item("rect_temp")
        collapse = wfc.Collapse(grid, cell)
        if(not collapse):
            dpg.delete_item("drawlist_main", children_only=True)
            grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
        else:
            wfc.Propagate(grid, collapse)
            dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
        
        cell = wfc.Select(grid)
        dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))
        for state in cell.possibleStates:
            dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())


    if(dpg.get_value("checkbox_animate")):
        toDraw = []
        while i < len(grid.grid):
            collapse = wfc.Collapse(grid)
            if(not collapse):
                dpg.delete_item("drawlist_main", children_only=True)
                grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
                toDraw = []
                i = 0
            else:
                wfc.Propagate(grid, collapse)
                if(dpg.get_value("checkbox_showAll")):
                    dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
                else: toDraw.append(collapse)
            i += 1
        if(not dpg.get_value("checkbox_showAll")):
            for collapse in toDraw:
                dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
    else:
        with dpg.window(label="Manual Control", autosize=True, tag="window_manual"):
            cell = wfc.Select(grid)
            dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))

            dpg.add_button(label="Step", tag="button_step", width=50, height=25, callback=button_stepCB)
            dpg.add_text("Select a tile to manually collapse this cell")
            dpg.add_group(horizontal=True, tag="group_manual")
            for state in cell.possibleStates:
                dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())

with dpg.viewport_menu_bar():
    with dpg.menu(label="File", tag="menu_file"):
        dpg.add_menu_item(label="Create New Tiles", callback=menu_loadImagesCB, tag="menu_loadImages")
        dpg.add_menu_item(label="Load Tiles", callback=menu_loadDataCB, tag="menu_LoadData")
    with dpg.menu(label="Settings", tag="menu_settings"):
        dpg.add_menu_item(label="Start Settings", callback=menu_startSettingsCB, tag="menu_startSettings")
    with dpg.menu(label="Run"):
        dpg.add_menu_item(label="Start", callback=menu_startCB, tag="menu_start")


dpg.create_viewport(title="Wavefunction Collapse Project", width=width, height=height, resizable=False)
dpg.add_viewport_drawlist(tag="drawlist_main", front=False)
dpg.add_texture_registry(tag="tex_register_main", show=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.show_metrics()
dpg.destroy_context()