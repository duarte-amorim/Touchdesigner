# me - this DAT
# scriptOp - the OP which is cooking
import os
import time
import string

# Change the name here if you change the name of the script operator
op_script_name = ''

# Pulse counts of Lightpulse button
light_pulse_count = 1
previous_brightness = -1
previous_layout = -1

previous_dru_label_number = 0
previous_key_label_number = 0
previous_use_label_number = 0

previous_dru_folder = None
previous_key_folder = None
previous_use_folder = None

previous_midi_op_name = None

dru_menu_files = ""
key_menu_files = ""
use_menu_files = ""


error_message = ["OOPS!! no folder or no .syx files"]
error_message2 = ["NO MIDI OUT CHOP"]
error_message3 = ["MIDI OUT CHOP NOT ACTIVE"]

 
def onSetupParameters(scriptOp):
    # Create Page
    page = scriptOp.appendCustomPage('Launchpad SysEx')

    # Midi
    scriptOp.clear()
    page.appendHeader("Header0", label='Midi')
    page.appendCHOP('Midiout', label='Midi Out Chop')

    # Layout Select
    sel = page.appendHeader('Header1', label='Layout Select')
    sel[0].startSection = True
    lay=page.appendHeader('Header2', label='Session/Default=0  Drums=1  Keys=2  User=3  Programmer Mode=4')
    lay = page.appendInt('Layout')
    lay[0].normMin = 0
    lay[0].normMax = 4
    lay[0].default = 0

    # Programs
    pro = page.appendHeader('Header3', label='Programs')
    pro[0].startSection = True

    page.appendToggle('Autosend', label='Auto Send Programs')
    page.appendToggle('Autolayout', label='Auto Select Layout')
    
    # Drums
    dru_menu = page.appendMenu('Drumsprog', label='Drums Program')
    dru_menu[0].menuLabels = dru_menu_files

    
    # Keys
    key_menu = page.appendMenu('Keysprog', label='Keys Program')
    key_menu[0].menuLabels = key_menu_files

    
    # User
    use_menu = page.appendMenu('Userprog', label='User Program')
    use_menu[0].menuLabels = use_menu_files

    # Resend
    page.appendPulse('Resendprog', label='ReSend All Selected Programs')
    
    # Folders
    page.appendFolder ('Drumsfolder', label='Drums SysEx Folder')
    page.appendFolder ('Keysfolder', label='Key SysEx Folder')
    page.appendFolder ('Userfolder', label='User SysEx Folder')

    # Light
    ligh = page.appendHeader('Header4', label='Light')
    ligh[0].startSection = True
    page.appendPulse('Light', label='Light on/off')

    # Brightness
    bri = page.appendInt('Brightness')
    bri[0].normMin = 0
    bri[0].normMax = 127
    bri[0].default = 127

    # Text Scrolling
    messag = page.appendHeader('Header5', label='Text Scrolling')
    messag[0].startSection = True
    page.appendStr('Text', label='Text Message')
    
    col = page.appendInt('Colour')
    col[0].normMin = 0
    col[0].normMax = 126
    col[0].default = 2
    
    spe = page.appendInt('Speed')
    spe[0].normMin = 0
    spe[0].normMax = 78
    spe[0].default = 10
    
    page.appendToggle('Loop', label='Loop')
    page.appendPulse('Start', label='Play Message')
    page.appendPulse('Stop', label='Stop Message')

    # Special Sysex
    spe_sysex = page.appendHeader('Header6', label='Special SysEx Message')
    spe_sysex[0].startSection = True
    page.appendStr('Messagesysex', label='Hexadecimal SysEx Message')
    page.appendPulse('Sendspsysex', label='Send Special Sysex')

    # Website
    website = page.appendHeader('Header7', label=' ')
    website[0].startSection = True
    page.appendPulse('Web', label="Made with 'love' by Duarte Amorim")
    page.appendHeader('Header8', label=' ')

    return page

def onSetupParameters_Drums(scriptOp):
    page = scriptOp.appendCustomPage('Launchpad SysEx')
    dru_menu = page.appendMenu('Drumsprog', label='Drums Program')
    dru_menu[0].menuLabels = dru_menu_files
    page.appendFolder ('Drumsfolder', label='Drums SysEx Folder')
    return

def onSetupParameters_Keys(scriptOp):
    page = scriptOp.appendCustomPage('Launchpad SysEx')
    key_menu = page.appendMenu('Keysprog', label='Keys Program')
    key_menu[0].menuLabels = key_menu_files
    page.appendFolder ('Keysfolder', label='Key SysEx Folder')
    return

def onSetupParameters_User(scriptOp):
    page = scriptOp.appendCustomPage('Launchpad SysEx')
    use_menu = page.appendMenu('Userprog', label='User Program')
    use_menu[0].menuLabels = use_menu_files
    page.appendFolder ('Userfolder', label='User SysEx Folder')
    return


def labels_sort(name):
    # Extract the numeric part by splitting on underscores
    parts = name.split("_")
    # Convert numeric parts to integers
    numeric_parts = [int(part) for part in parts if part.isdigit()]
    # If there are no numeric parts, assume a numeric part of 0
    if not numeric_parts:
        numeric_parts = [0]
    # Return a tuple of numeric parts and the original file name
    return (numeric_parts, name)



## --------------------------------------------------------------------------------------------------
## --------------------------------------------------------------------------------------------------

def onCook(scriptOp):		
    global previous_layout, op_script_name, previous_brightness, previous_midi_op_name, previous_dru_label_number, previous_key_label_number, previous_use_label_number, previous_dru_folder, previous_key_folder, previous_use_folder

    op_script_name = scriptOp.name
    midi_op_name = scriptOp.par.Midiout
    
    if midi_op_name != None:
        n = op(str(midi_op_name))

        if op(str(midi_op_name)).par.active == False and op(str(midi_op_name)).type == "midiout":
            onSetupParameters_Drums(scriptOp)
            onSetupParameters_Keys(scriptOp)
            onSetupParameters_User(scriptOp)
            scriptOp.par.Drumsprog.menuLabels = error_message3
            scriptOp.par.Keysprog.menuLabels = error_message3
            scriptOp.par.Userprog.menuLabels = error_message3
            previous_dru_folder = None
            previous_key_folder = None
            previous_use_folder = None

        else:

        
        ## -------------- BRIGHTNESS --------------
        
            brightness = int(scriptOp.par.Brightness)	
            if brightness != previous_brightness:
                if 0 <= brightness <= 127:
              
                    bright_number = int(scriptOp.par.Brightness)
                    bright_number = format(bright_number, '02X')
                    bright_sysex = "F0002029020D08" + bright_number + "F7"
                    # Convert bright_sysex hex to bytes
                    sysex_bytes_bright = bytes.fromhex(bright_sysex)

                    bright_number = int(scriptOp.par.Brightness)
                    bright_number = format(bright_number, '02X')
                    bright_sysex = "F0002029020D08" + bright_number + "F7"
                    # Convert bright_sysex hex to bytes
                    sysex_bytes_bright = bytes.fromhex(bright_sysex)
                    n.send(sysex_bytes_bright)
                else:
                    print('Brightness out of range. It should be within the range of 0 to 127.')

                previous_brightness = brightness


        ## -------------- LAYOUT SELECT --------------

            layout = int(scriptOp.par.Layout)	
            if layout != previous_layout:
                if 0 <= layout <= 4:
            
                    layout_number = int(scriptOp.par.Layout)
                    if layout_number == 0:
                        layout_number = "00"
                    elif 1 <= layout_number <= 3:
                        layout_number = layout_number + 3
                        layout_number = f'{layout_number:02}'
                    elif layout_number == 4:
                        layout_number = "7F"
                        
                    layout_sysex = "F0002029020D00" + str(layout_number) + "F7"
                    sysex_bytes_layout = bytes.fromhex(layout_sysex)

                    n.send(sysex_bytes_layout)
                previous_layout = layout



        ## -------------- DRUMS -------------- KEYS -------------- USER --------------

            # Drums Keys User Labels
            dru_folder = str(scriptOp.par.Drumsfolder)
            key_folder = str(scriptOp.par.Keysfolder)
            use_folder = str(scriptOp.par.Userfolder)
            
            # Label Path Folder
            dru_folder_path = scriptOp.par.Drumsfolder.eval()
            key_folder_path = scriptOp.par.Keysfolder.eval()
            use_folder_path = scriptOp.par.Userfolder.eval()

            dru_menu_files = error_message
            key_menu_files = error_message
            use_menu_files = error_message

            dru_label = scriptOp.par.Drumsprog
            key_label = scriptOp.par.Keysprog
            use_label = scriptOp.par.Userprog

            dru_syx_found = False
            key_syx_found = False
            use_syx_found = False

            dru_file_bytes = bytes.fromhex("F0002029020DF7")
            key_file_bytes = bytes.fromhex("F0002029020DF7")
            use_file_bytes = bytes.fromhex("F0002029020DF7")

            auto_send = scriptOp.par.Autosend
            resend = scriptOp.par.Resendprog

            scriptOp_name = scriptOp.name

            
            # DRUMS ------------------------------------------------

            # Iterate through the files in the folder
            if os.path.exists(dru_folder_path):
                for file_name in os.listdir(dru_folder_path):
                    if file_name.endswith(".syx"):
                        dru_syx_found = True
                        break
            if (dru_folder != previous_dru_folder) or dru_label  == "":      
                # Empty labels
                onSetupParameters_Drums(scriptOp)        
                # Check if the folder exists and is not empty                
                if dru_folder_path and os.path.exists(dru_folder_path) and os.listdir(dru_folder_path) and dru_syx_found == True:
                    # Get the list of file names in the folder
                    dru_file_names = os.listdir(dru_folder_path)
                    # Filter for .syx files, sort them with the custom labels_sort function
                    dru_syx_files = sorted([f for f in dru_file_names if f.endswith('.syx')], key=labels_sort)
                    # Set the menu labels to the extracted values
                    dru_menu_files = dru_syx_files
                    # Refresh new labels
                    scriptOp.par.Drumsprog.menuLabels = dru_menu_files
                    previous_dru_label_number = -1
                else:
                    # Set the menu labels to the extracted values
                    dru_menu_files = error_message
                    # Refresh new labels
                    scriptOp.par.Drumsprog.menuLabels = dru_menu_files
                previous_dru_folder = dru_folder

            if (dru_label != "" and dru_label != error_message):
                dru_file = str(scriptOp.par.Drumsprog.eval())
                dru_label_number = int(scriptOp.par.Drumsprog)

            if dru_folder_path and os.path.exists(dru_folder_path) and os.listdir(dru_folder_path) and dru_syx_found == True:
                dru_all_path = dru_folder + "/" + dru_file
                with open(dru_all_path, "rb") as file:
                    dru_bytes_file = file.read()
                dru_hex_file = dru_bytes_file.hex()
                char_dru_hex_list = list(dru_hex_file)
                char_dru_hex_list[20] = '0'
                char_dru_hex_list[21] = '4'
                final_dru_hex = ''.join(char_dru_hex_list)
                dru_file_bytes = bytes.fromhex(final_dru_hex)
                if (dru_label_number != previous_dru_label_number):
                    if dru_label_number >= 0 and auto_send == True:
                        n.send(dru_file_bytes)
                        if scriptOp.par.Autolayout == True:
                            layout_dru = "F0002029020D0004F7"
                            layout_dru_bytes = bytes.fromhex(layout_dru)
                            n.send(layout_dru_bytes)
                    previous_dru_label_number = dru_label_number
                                   


            # KEYS ------------------------------------------------

            if os.path.exists(key_folder_path):
                for file_name in os.listdir(key_folder_path):
                    if file_name.endswith(".syx"):
                        key_syx_found = True
                        break
            if (key_folder != previous_key_folder) or key_label  == "":
                    onSetupParameters_Keys(scriptOp)
                    
                    if key_folder_path and os.path.exists(key_folder_path) and os.listdir(key_folder_path) and key_syx_found == True:
                        key_file_names = os.listdir(key_folder_path)
                        key_syx_files = sorted([f for f in key_file_names if f.endswith('.syx')], key=labels_sort)
                        key_menu_files = key_syx_files
                        scriptOp.par.Keysprog.menuLabels = key_menu_files
                        previous_key_label_number = -1
                    else:
                        key_menu_files = error_message
                        scriptOp.par.Keysprog.menuLabels = key_menu_files
                    previous_key_folder = key_folder

            if (key_label != "" and key_label != error_message):
                key_file = str(scriptOp.par.Keysprog.eval())
                key_label_number = int(scriptOp.par.Keysprog)

            if key_folder_path and os.path.exists(key_folder_path) and os.listdir(key_folder_path) and key_syx_found == True:
                key_all_path = key_folder + "/" + key_file	
                with open(key_all_path, "rb") as file:
                    key_bytes_file = file.read()
                key_hex_file = key_bytes_file.hex()
                char_key_hex_list = list(key_hex_file)
                char_key_hex_list[20] = '0'
                char_key_hex_list[21] = '5'
                final_key_hex = ''.join(char_key_hex_list)
                key_file_bytes = bytes.fromhex(final_key_hex)
                if (key_label_number != previous_key_label_number):
                    if key_label_number >= 0 and auto_send == True:
                        n.send(key_file_bytes)
                        if scriptOp.par.Autolayout == True:
                            layout_key = "F0002029020D0005F7"
                            layout_key_bytes = bytes.fromhex(layout_key)
                            n.send(layout_key_bytes)
                    previous_key_label_number = key_label_number



            # USER ------------------------------------------------

            if os.path.exists(use_folder_path):
                for file_name in os.listdir(use_folder_path):
                    if file_name.endswith(".syx"):
                        use_syx_found = True
                        break
            if (use_folder != previous_use_folder) or use_label  == "":
                    onSetupParameters_User(scriptOp)
                    
                    if use_folder_path and os.path.exists(use_folder_path) and os.listdir(use_folder_path) and use_syx_found == True:
                        use_file_names = os.listdir(use_folder_path)
                        use_syx_files = sorted([f for f in use_file_names if f.endswith('.syx')], key=labels_sort)
                        use_menu_files = use_syx_files
                        scriptOp.par.Userprog.menuLabels = use_menu_files
                        previous_use_label_number = -1
                    else:
                        use_menu_files = error_message
                        scriptOp.par.Userprog.menuLabels = use_menu_files
                    previous_use_folder = use_folder

            if (use_label != "" and use_label != error_message):
                use_file = str(scriptOp.par.Userprog.eval())
                use_label_number = int(scriptOp.par.Userprog)

            if use_folder_path and os.path.exists(use_folder_path) and os.listdir(use_folder_path) and use_syx_found == True:
                use_all_path = use_folder + "/" + use_file	
                with open(use_all_path, "rb") as file:
                    use_bytes_file = file.read()
                use_hex_file = use_bytes_file.hex()
                char_use_hex_list = list(use_hex_file)
                char_use_hex_list[20] = '0'
                char_use_hex_list[21] = '6'
                final_use_hex = ''.join(char_use_hex_list)
                use_file_bytes = bytes.fromhex(final_use_hex)
                if (use_label_number != previous_use_label_number):
                    if use_label_number >= 0 and auto_send == True:
                        n.send(use_file_bytes)
                        if scriptOp.par.Autolayout == True:
                            layout_use = "F0002029020D0006F7"
                            layout_use_bytes = bytes.fromhex(layout_use)
                            n.send(layout_use_bytes)
                    previous_use_label_number = use_label_number

            return (dru_file_bytes, key_file_bytes, use_file_bytes, scriptOp)

        
    else:
        onSetupParameters_Drums(scriptOp)
        onSetupParameters_Keys(scriptOp)
        onSetupParameters_User(scriptOp)
        scriptOp.par.Drumsprog.menuLabels = error_message2
        scriptOp.par.Keysprog.menuLabels = error_message2
        scriptOp.par.Userprog.menuLabels = error_message2
        previous_dru_folder = None
        previous_key_folder = None
        previous_use_folder = None

    scriptOp.clear()
        


def find_non_hex_character_position(s):
    try:
        bytes.fromhex(s)
        return None  # No exception raised, it's valid hex
    except ValueError as e:
        error_message = str(e)
        # Extract the position from the error message
        if "at position" in error_message:
            position_str = error_message.split("at position")[1].strip()
            if position_str.isdigit():
                position = int(position_str)
                return position
        return None

def insert_spaces_at_position(s, position):
    if position is not None:
        if 0 <= position < len(s):
            return s[:position] + " " + s[position] + " " + s[position + 1:]
    return s

## --------------------------------------------------------------------------------------------------
## --------------------------------------------------------------------------------------------------

def onPulse(par):
    global op_script_name, light_pulse_count, op_script_name
        
    scriptOp = op(str(op_script_name))
    midi_op_name = scriptOp.par.Midiout

    if midi_op_name != None:
        n = op(str(midi_op_name))

        dru_file_bytes = onCook(scriptOp)
        key_file_bytes = onCook(scriptOp)
        use_file_bytes = onCook(scriptOp)

## -------------- RESEND --------------
        
        if par.name == 'Resendprog':
            n.send(dru_file_bytes[0])
            n.send(key_file_bytes[1])
            n.send(use_file_bytes[2])

## -------------- SPECIAL SYSEX MESSAGE --------------

        special_sysex_mes = str(scriptOp.par.Messagesysex.eval())
        special_sysex_mes = special_sysex_mes.replace(" ", "")
        if par.name == 'Sendspsysex' and special_sysex_mes != "":
            if len(special_sysex_mes) % 2 == 0:
                if par.name == 'Sendspsysex':
                    position = find_non_hex_character_position(special_sysex_mes)
                    if position is not None:
                        special_sysex_mes_spaced = insert_spaces_at_position(special_sysex_mes, position)
                        ui.messageBox('Special SysEX Message', f"The SysEx message you've written contains non-hexadecimal characters. \n\nError: Non-hexadecimal character found at position {position} \n\nPlease rewrite it, and don't forget to include 'F0' at the beginning and 'F7' at the end. \n:)")
                        print (f"Error: Non-hexadecimal character found at position {position} in the message:\n{special_sysex_mes_spaced}")
                    else:
                        special_sysex_mes_bytes = bytes.fromhex(special_sysex_mes)
                        n.send(special_sysex_mes_bytes)
                        print("Special SysEx Message Sent")
            else:
                ui.messageBox('Special SysEX Message', "The SysEx message you've written must be a string with an even number of characters. \nPlease rewrite it, and don't forget to include 'F0' at the beginning and 'F7' at the end. \n:)")
                print("The SysEx message you've written must be a string with an even number of characters.")

            

## -------------- LIGHT --------------
        # Light sysex hex_light_1 = off and hex_light_2 = on
        hex_light = ""
        hex_light_1 = "F0002029020D0900F7"
        hex_light_2 = "F0002029020D0901F7"

        # Handle pulses for the "Light" button
        if par.name == 'Light':
            light_pulse_count += 1  
            # Increment the pulse count for 'Light'
            if light_pulse_count % 2 == 0:
                hex_light = hex_light_1
            else:
                hex_light = hex_light_2

        # Convert hex_light hex to bytes
        sysex_bytes_light = bytes.fromhex(hex_light)

        # If Pulse on = send sysex
        if par.name == 'Light':
            n.send(sysex_bytes_light)


## -------------- TEXT SCROLLING --------------

        #text_message
        loop_toggle = scriptOp.par.Loop.eval()
        write_text = str(scriptOp.par.Text.eval())

        if write_text == "":
            write_text_hex = "454D505459"
        else: 
            write_text_hex = ''.join(f'{ord(char):02x}' for char in write_text)
        
        #text_colour
        colour_number = int(scriptOp.par.Colour)+1
        text_colour = format(colour_number, '02X') # Convert text to hex
        
        #text_speed
        speed_number = int(scriptOp.par.Speed)+1
        text_speed = "{:02}".format(speed_number) #allways 2 digits "01...79"

        #text_loop
        if loop_toggle: 
            text_loop = "01"
        else:
            text_loop = "00"


        #text_play
        if par.name == 'Start':
            if 1 <= colour_number <= 127 and 1 <= speed_number <= 79:
                play_message = "F0002029020D07" + text_loop + text_speed + "00" + text_colour + write_text_hex + "F7"
                play_message_bytes = bytes.fromhex(play_message)
                n.send(play_message_bytes)
            else:
                print('Colour or Speed out of range. They should be within the ranges of 0 to 126 for Colour and 0 to 78 for Speed.')

        #text_stop
        stop_message = "F0002029020D070040000320F7"
        stop_message_bytes = bytes.fromhex(stop_message)
        
        if par.name == 'Stop':
            n.send(stop_message_bytes)

        if op(str(midi_op_name)).par.active == False and op(str(midi_op_name)).type == "midiout":
            print("Unable to send the message. \nOperator MIDI Out is not ACTIVE.")

    else:
        if par.name != 'Web':
            print("Unable to send the message. \nNo operator MIDI Out is selected in the 'Midi Out Chop' on this page.")




## -------------- WEB --------------
            
    duarte = "https://www.duarteamorim.com/"
    if par.name == 'Web':
        ui.viewFile(duarte)


    return
