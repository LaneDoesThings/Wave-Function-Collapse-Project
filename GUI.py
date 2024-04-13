import dearpygui.dearpygui as dpg
import json
from PIL import Image
import numpy as np
from WFC import WaveFunctionCollapse as wfc
from WFC import Grid, Tile

dpg.create_context()

#Change the size of the window here
width, height = 1920, 1080
sideData: dict = {}

def menu_loadImagesCB(sender, app_data, user_data):
    '''
    Callback for loading and creating a new set of tiles to
    be used in the wave function collapse algorithm
    '''

    images: list[list] = [] #List of the images the user inputs

    def file_loadImagesCB(sender, app_data, user_data):
        '''
        Inner-Callback to load the images after the user has selected them
        '''

        #For every image the user selected get its data and append it to the images list
        for path in app_data["selections"].values():
            width, height, channels, data = dpg.load_image(path)
            images.append([path, dpg.add_static_texture(parent="tex_register_main", width=width, height=height, default_value=data)])
        dpg.delete_item("file_loadImages") #Delete the reference to the file explorer

        def menu_saveSidesCB(sender, app_data, user_data):
            '''
            Inner-Callback to save the tile data as a json file
            for loading in to the algorithm
            '''

            global sideData

            dpg.delete_item("window_setSides")
            #The path where the images are saved
            #Saved as the absolute path which isn't the best
            #but I can't change that
            path = list(app_data["selections"].values())[0] 

            #Open a json file and save the tile data
            with open(f"{path}.json", "w") as outfile:
                json.dump(sideData, outfile)
        
        def button_image_imageSelectCB(sender, app_data, user_data):
            '''
            Inner-Callback that prompts the user to enter the data for the selected tile
            '''

            def button_setCB(sender, app_data, user_data):
                '''
                Inner-Callback for updating interal representation of tile data
                with the data entered by the user
                '''

                global sideData

                #Set the internal side data with the data input by the user
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

            #Create a window that prompts the user to enter the side data for the selected image
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

        #Window that allows the user to select an image to set the data for
        with dpg.window(label="Set Sides", autosize=True, tag="window_setSides"):
            with dpg.menu_bar():
                dpg.add_menu_item(label="Save", callback=lambda: dpg.add_file_dialog(directory_selector=True, width=720, height=480, callback=menu_saveSidesCB), tag="menu_saveSides")
            
            dpg.delete_item("button_image")

            with dpg.child_window(width=100, height=400, tag="window_child_setSides"):
                for data in images:
                    dpg.add_image_button(texture_tag=data[1], width=50, height=50, callback=button_image_imageSelectCB, user_data=data)

    #Open the file explorer for png files
    with dpg.file_dialog(directory_selector=False, callback=file_loadImagesCB, tag="file_loadImages", file_count=20, width=720, height=480):
        dpg.add_file_extension(".png")

def menu_loadDataCB(sender, app_data, user_data):
    '''
    Callback that will handle the loading of the json file
    which holds the tile data
    '''

    def file_loadDataCB(sender, app_data, user_data):
        '''
        Inner-Callback that gets called once the user selects a file
        '''


        def button_rotateCB(sender, app_data, user_data):
            '''
            Inner-Callback for prompting the user on how many rotations a
            tile should have
            '''


            def button_setRotationsCB(sender, app_data, user_data):
                '''
                Inner-Callback that does the rotations on a tile based on
                the number specified by the user
                '''

                #Get the image data from the previous callback
                #and rotate the selected image the amount the user specified
                rawImage, PILImage, image = user_data
                for i in range(1, dpg.get_value("input_int_rotationAmount")):
                    data = np.asfarray(PILImage.rotate(-90 * i), dtype='f') #Load the image and rotate it using numpy and pillow
                    textureData = np.true_divide(data, 255.0) #Puts the rotated image data in a format dearpygui can read
                    #Turn the rotated data into a dearpygui raw texture
                    rawImage = dpg.add_raw_texture(parent="tex_register_main", width=PILImage.width, height=PILImage.height, default_value=textureData, format=dpg.mvFormat_Float_rgba, tag=rawImage + "_rotate")
                    #Rotate the side data of the newly created tile
                    sideData[rawImage] = {
                        "up": image["left"],
                        "down": image["right"],
                        "left": image["down"],
                        "right": image["up"]
                    }
                    image = sideData[rawImage] #Setup the next image to be rotated
                    dpg.delete_item("window_rotation")
                    dpg.show_item("window_rotateSelection")

            dpg.hide_item("window_rotateSelection")

            #Window to ask the user how many rotatations should be done on a tile
            with dpg.window(label="Rotations", autosize=True, tag="window_rotation"):
                dpg.add_image(texture_tag=user_data[0], width=50, height=50)
                dpg.add_text(label="How many rotatons?")
                dpg.add_input_int(tag="input_int_rotationAmount")
                dpg.add_button(label="Set", callback=button_setRotationsCB, user_data=user_data)
            
            dpg.delete_item(sender)
                    
        global sideData

        #The path where the images are saved
        #Saved as the absolute path which isn't the best
        #but I can't change that
        path = list(app_data["selections"].values())[0]

        #Load the json data
        with open(path) as f:
            sideData = json.load(f)
        dpg.delete_item("file_loadData")

        images = []
        #For all the sides of a tile get its data and turn it into a dearpygui texture
        for sides in sideData.values():
            image = Image.open(sides["path"]).convert("RGBA") #Open the image as a pillow image
            data = np.asfarray(image, dtype='f') #Convert it to a numpy array
            textureData = np.true_divide(data, 255.0) #Turn it into a format usable by dearpygui
            #Save the image as a dearpygui raw texture
            rawImage = dpg.add_raw_texture(parent="tex_register_main", width=image.width, height=image.height, default_value=textureData, format=dpg.mvFormat_Float_rgba, tag=list(sideData.keys())[list(sideData.values()).index(sides)])
            images.append([rawImage, image, sides]) #Append it to the list of images

        #Create a window that allows the user to select tiles that need to be rotated
        with dpg.window(label="Select Rotatations", tag="window_rotateSelection", autosize=True):
            dpg.add_text(label="Select the tiles that need to be rotated.")
            with dpg.group(horizontal=True):
                for data in images:
                    dpg.add_image_button(data[0], label="Rotate", width=50, height=50, callback=button_rotateCB, user_data=data)

    with dpg.file_dialog(directory_selector=False, callback=file_loadDataCB, tag="file_loadData", file_count=20, width=720, height=480):
        dpg.add_file_extension(".json")

def menu_startSettingsCB(sender, app_data, user_data):
    '''
    Callback that shows the settings for running the algorithm
    '''
    
    dpg.delete_item("window_settings")
    #Create a window witht the settings
    with dpg.window(label="Settings", autosize=True, tag="window_settings"):
        dpg.add_checkbox(label="Show full process (Warning Possible Flashing Lights)", default_value=False, tag="checkbox_showAll")
        dpg.add_checkbox(label="Animate", default_value=True, tag="checkbox_animate")

def menu_startCB(sender, app_data, user_data):
    '''Callback that starts the algorthim based on the settings from the user'''

    global sideData, grid, i, cell

    grid = Grid(width, height, 50, Tile.ParseTiles(sideData)) #Create a grid to be used for wfc
    i = 0 #Used for reseting the grid if a conflict is found and stopping when the grid is full

    def button_manualCB(sender, app_data, user_data):
        '''
        Inner-Callback that handles when a user manually collapses the next cell
        '''
        global grid, cell

        dpg.delete_item("group_manual", children_only=True)
        dpg.delete_item("rect_temp")
        collapse = wfc.ManualCollapse(cell, user_data) #Collapse the cell with the option the user picked
        #If it isn't possible reset the grid
        if(not collapse):
            dpg.delete_item("drawlist_main", children_only=True)
            grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
        #Otherwise propagate the change and draw the tile
        else:
            wfc.Propagate(grid, collapse)
            dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))

        #Select a new cell
        cell = wfc.Select(grid)
        dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))
        for state in cell.possibleStates:
            dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())

    def button_stepCB(sender, app_data, user_data):
        '''
        Inner-Callback that steps the algorithm
        '''

        global grid, cell

        dpg.delete_item("group_manual", children_only=True)
        dpg.delete_item("rect_temp")
        collapse = wfc.Collapse(grid, cell) #Collapse the cell
        #If it isn't possible reset the grid
        if(not collapse):
            dpg.delete_item("drawlist_main", children_only=True)
            grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
        #Otherwise propagate the change and draw the tile
        else:
            wfc.Propagate(grid, collapse)
            dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
        
        #Select a new cell
        cell = wfc.Select(grid)
        dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))
        for state in cell.possibleStates:
            dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())


    #If the user wants the algorithm animated
    if(dpg.get_value("checkbox_animate")):
        toDraw = [] # Create a list to store the finished grid
        #While there are still cells to collapse
        while i < len(grid.grid):
            collapse = wfc.Collapse(grid) #Collapse a cell
            #If not possible reset the grid
            if(not collapse):
                dpg.delete_item("drawlist_main", children_only=True)
                grid = Grid(grid.width, grid.height, grid.step, grid.tiles)
                toDraw = []
                i = 0
            #Otherwise propagate the cell
            else:
                wfc.Propagate(grid, collapse)
                if(dpg.get_value("checkbox_showAll")): #If the user wants to see the whole proccess draw the tile now
                    dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
                else: toDraw.append(collapse)
            i += 1
        #The user just wanted to see the end product
        if(not dpg.get_value("checkbox_showAll")):
            for collapse in toDraw:
                dpg.draw_image(parent="drawlist_main", texture_tag=collapse.state.tag, pmin=(collapse.position[0], collapse.position[1]), pmax=(collapse.position[0] + grid.step, collapse.position[1] + grid.step))
    #The user wanted to manually step through the algorithm
    else:
        #Create a window for manually controlling the algorithm
        with dpg.window(label="Manual Control", autosize=True, tag="window_manual"):
            cell = wfc.Select(grid)
            dpg.draw_rectangle(parent="drawlist_main", pmin=cell.position, pmax=[cell.position[0] + grid.step, cell.position[1] + grid.step], color=(255, 0, 0, 255))

            #Add a step button and the possible options for the current cell if the user
            #wants to manually set the state
            dpg.add_button(label="Step", tag="button_step", width=50, height=25, callback=button_stepCB)
            dpg.add_text("Select a tile to manually collapse this cell")
            dpg.add_group(horizontal=True, tag="group_manual")
            for state in cell.possibleStates:
                dpg.add_image_button(parent="group_manual", texture_tag=state.tag, width=50, height=50, callback=button_manualCB, user_data=state, tag=dpg.generate_uuid())

#The top menu
with dpg.viewport_menu_bar():
    with dpg.menu(label="File", tag="menu_file"):
        dpg.add_menu_item(label="Create New Tiles", callback=menu_loadImagesCB, tag="menu_loadImages")
        dpg.add_menu_item(label="Load Tiles", callback=menu_loadDataCB, tag="menu_LoadData")
    with dpg.menu(label="Settings", tag="menu_settings"):
        dpg.add_menu_item(label="Start Settings", callback=menu_startSettingsCB, tag="menu_startSettings")
    with dpg.menu(label="Run"):
        dpg.add_menu_item(label="Start", callback=menu_startCB, tag="menu_start")


#Create the application and start dearpygui
dpg.create_viewport(title="Wavefunction Collapse Project", width=width, height=height, resizable=False)
dpg.add_viewport_drawlist(tag="drawlist_main", front=False)
dpg.add_texture_registry(tag="tex_register_main", show=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.show_metrics()
dpg.destroy_context()