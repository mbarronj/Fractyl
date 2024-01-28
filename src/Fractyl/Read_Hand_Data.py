# pyright: reportMissingImports=false, reportUnusedVariable=false, reportUndefinedVariable=false
# Clearning error warnings for now - should really just install PySide. . .
# -*- coding: utf-8 -*-
import os.path
import PySide
import json
from PySide import QtGui ,QtCore
from PySide.QtGui import *
from PySide.QtCore import *

import FreeCAD as App

path = App.ConfigGet("UserAppData")

def readHandData():
    OpenName = None
    finger_data = None
    # Check for default file
    default_path = "Macro\\Fractyl\\default_hand.json"
    if os.path.isfile(path + default_path):
        OpenName = path + default_path
        App.Console.PrintMessage(f"ReadHandData: default hand geometry found at {default_path}\n")
    
    if OpenName is None:
        OpenName = ""
        App.Console.PrintMessage("ReadHandData: Attempting to Open File Dialog\n")
        try:
            OpenName = QFileDialog.getOpenFileName(None,QString.fromLocal8Bit("Read a JSON file"),path,"*.json") # PyQt4
        #                                                                     "here the text displayed on windows" "here the filter (extension)"   
        except Exception:
            OpenName, Filter = PySide.QtGui.QFileDialog.getOpenFileName(None, "Read a JSON file", path,"*.json") #PySide
    #                                                                     "here the text displayed on windows" "here the filter (extension)"   
    if OpenName == "":                                                            # if the name file are not selected then Abord process
        App.Console.PrintMessage("Process aborted"+"\n")
        return None
    else:
        App.Console.PrintMessage("Reading "+OpenName+"\n")                        # text displayed to Report view (Menu > View > Report view checked)
        try:                                                                      # detect error to read file
            file = open(OpenName, "r")                                            # open the file selected to read (r)  # (rb is binary)
            try:                                                                  # detect error ...
                # Read JSON data
                try:
                    finger_data = json.load(file)
                except json.JSONDecodeError as e:
                    App.Console.PrintMessage(f"File: {e.doc} Parse error Line:{e.lineno}")
                    #JSONDecodeError
                
                op = OpenName.split("/")                                          # decode the path
                op2 = op[-1].split(".")                                           # decode the file name 
                nomF = op2[0]                                                     # the file name are isolated

                App.Console.PrintMessage(str(nomF)+"\n")                          # the file name are displayed

            except Exception:                                                     # if error detected to read
                App.Console.PrintError("Error reading file "+"\n")                   # detect error ... display the text in red (PrintError)
            finally:                                                              # if error detected to read ... or not error the file is closed
                file.close()                                                      # if error detected to read ... or not error the file is closed
        except Exception:                                                         # if one error detected to read file
            App.Console.PrintError("Error Opening the file "+OpenName+"\n")       # if one error detected ... display the text in red (PrintError)
    # return data to calling function
    return finger_data

if __name__ == "main":
    print("Not Implemented as Standalone")