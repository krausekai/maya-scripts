"""

For Windows OS, Python 2.6, Maya 2012

-----------------------------------------------------------------------------------

The MIT License

Copyright (c) 2014 Kai Krause <kaikrause95@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import maya.cmds as cmds
import maya.mel as mel
from xml.dom.minidom import Document
from xml.dom.minidom import parse
import os #operating system interaction - https://docs.python.org/2/library/os.html
import re #regular expressions - https://docs.python.org/2/library/re.html
import shutil #Copy and move files - https://docs.python.org/2/library/shutil.html

global fileBrowserPath
fileBrowserPath = os.path.expanduser('~')
global fileBrowserPathToSave
fileBrowserPathToSave = fileBrowserPath

#----------------------------------------------------------------------------------------------------------------------
# Thanks to http://stackoverflow.com/a/8692622
def raw_string(s):
    if isinstance(s, str):
        s = s.encode('string-escape')
    elif isinstance(s, unicode):
        s = s.encode('unicode-escape')
    return s
#----------------------------------------------------------------------------------------------------------------------
def fileBrowser(*args):
    global fileBrowserPath
    global fileBrowserPathToSave
    
    fileBrowserPath = cmds.fileDialog2(caption="Select A Unity Project Folder", fileMode= 3 , dialogStyle=2)
    if fileBrowserPath is not None:
        cmds.textField( 'fileBrowserTextField', edit=True, width=150, text=str(fileBrowserPath)[3:-2] )
        fileBrowserPathToSave = str(fileBrowserPath)[3:-2]
#----------------------------------------------------------------------------------------------------------------------

projectNameList = list()
itemToRemove = False
exportSave = False

def savePreferences(*args) :
    global loadedProjNameFolderList
    global itemToRemove
    global removeItemBool
    global exportSave
    
    continueToSave = False
    
    #check to see if the projectName text field is empty in a boolean fashion, empty is false
    if removeItemBool is False and exportSave is False and not cmds.textField('projectNameTextField', query=True, text=True) or not cmds.textField('fileBrowserTextField', query=True, text=True):
            continueToSave = False
            #create a popup dialog to warn the user about empty Project Name / Path
            cmds.confirmDialog(title="Project Name or Path Not Specified!",
                                message='You must specify a Project Name and Path to save!', button=['Okay!'] )
        
    else:
        continueToSave = True
        
    if continueToSave is True:
        #query the textField by name 'projectNameTextField' in order to obtain the user entered value
        #for our projectName and append to list our project name and path
        if removeItemBool is False:
            projectName = mel.eval('textField -q -text projectNameTextField  ')
            projectNameList.append(projectName  + " " + fileBrowserPathToSave)
        
        #create our xml document
        doc = Document()
        #name our document's root node of the hierarchy
        root_node = doc.createElement("kkexportsettings")
        
        #keep our loadedPreferences data from our previous session
        for loadedAttr in loadedProjNameFolderList:
                projectNameList.append(loadedAttr)
        
        #Append each child containing our data within the parent 'root' node consecutively
        doc.appendChild(root_node)
        
        #save our exporter checkbox settings
        exportSettingsList = ['cb_optimizeScene','cb_freezeTransformations','cb_centerPivots',
                              'cb_deleteHistory','cb_saveScene','cb_exportTextures','cb_smartExport','cb_ignoreAssetsSource']
        cb_eslStr = ''
        
        for esl in exportSettingsList:
            if cmds.checkBox(esl, query=True, value=True):
                cb_eslStr += str(esl+",")
            
        if cb_eslStr is not '':
            #create our child node elements and append them after another to our root node
            child_nodeA = doc.createElement("checkbox")
            root_node.appendChild(child_nodeA)
            
            #set our attributes based on the tag "name_path" with the attribute of 'each'
            child_nodeA.setAttribute("cb_settings", str(cb_eslStr))

        #Remove our Item
        for each in projectNameList:
            if each != itemToRemove:
                #create our child node elements and append them after another to our root node
                child_nodeB = doc.createElement("Project")
                root_node.appendChild(child_nodeB)
                
                #set our attributes based on the tag "name_path" with the attribute of 'each'
                child_nodeB.setAttribute("name_path", str(each))
        
        #Write our XML file to Maya's default script directory, Windows only
        mayaVersion = mel.eval('about -v')
        userProfile = os.path.expanduser('~') #returns the user's 'my documents' folder
        saveDir =  str(userProfile) + "//maya//" + str(mayaVersion) + "//scripts//"
        
        xml_file = open( str(saveDir) + "kkMayaToUnityExportSettings.xml", "w" )
        xml_file.write(doc.toprettyxml())
        xml_file.close()

        #delete our lists which populated the xml originally, so we don't have duplicates!
        del projectNameList[:]
        del loadedProjNameFolderList[:]
        
        #reset our item removal
        itemToRemove = None
        removeItemBool = False
        #reset our export save bool
        exportSave = False
        
        #recreate our GUI to refresh menu elements, in particular for our listing of projects
        createGUI_km2uet()

"""
#----------------------------------------------------------------------------------------------------------------------
"""
# Create a list of our project names and project folder paths from last session
loadedProjNameFolderList = list()
loadedcbsList = list ()

def loadPreferences(*args):
    global loadedProjNameFolderList
    global loadedProjNameFolderListLength
    global haveWeLoadedPreferences
    global dom
    global xmlFile
    global loadedcbsList
    
    del loadedProjNameFolderList[:]
    loadedProjNameFolderListLength = 0
    
    #Find and load our XML document
    #Windows OS only currently?
    mayaVersion = mel.eval('about -v')
    userProfile = os.path.expanduser('~') #returns the user's 'my documents' folder
    saveDir =  str(userProfile) + "//maya//" + str(mayaVersion) + "//scripts//"
    
    if os.path.exists(saveDir + "kkMayaToUnityExportSettings.xml"):
        xmlFile = saveDir + "kkMayaToUnityExportSettings.xml"
        
        #open and parse our xml file for reading
        dom = parse(xmlFile)
        
        # visit every child node and get it's attribute to append to our drop-down menu
        for child_nodes in dom.getElementsByTagName("Project"):
            x = child_nodes.getAttribute("name_path")
            loadedProjNameFolderList.append(x)
            loadedProjNameFolderListLength = len(loadedProjNameFolderList)
        
        # get our checkbox settings
        if dom.getElementsByTagName("checkbox") is not None:
            for cbs_s in dom.getElementsByTagName("checkbox"):
                y = cbs_s.getAttribute("cb_settings")
                loadedcbsList = y.split(',')
                
    haveWeLoadedPreferences = True

"""
#----------------------------------------------------------------------------------------------------------------------
"""
#-------------
# SELECT_ITEM
#-------------
def selectedMenuItem(selected):
    global selectedDropMenuPath
    
    if selected is not None:
        abcList = list()
        abcList.insert(0, selected)
        selectedDropMenuPath = abcList[0]
    if selected is None:
        selectedDropMenuPath = defaultMenuItem

#-------------
# EXPLORE_ITEM
#-------------
def exploreItem(*args):
    
    #Pass our list object to a string, then find the index of a singular character as an int
    #Minus this character ':' by -1 to account for drive letter, thus we have C: drive for eg
    purifyStr = str(selectedDropMenuPath)
    purifiedStr = purifyStr.index(":")-1
    
    #splice our string, removing all characters prior to the drive letter
    toOpen = str(purifyStr)[purifiedStr:]

    #startfile is windows only
    os.startfile ( str(toOpen) )

#-------------
# EXPLORE SAVED ITEM
#-------------
global exploreFilePath
exploreFilePath = ''

def exploreSavedItem(*args):
    os.startfile ( str(exploreFilePath) )

#-------------
# REMOVE_ITEM
#-------------
def removeItem(*args):
    global removeItemBool
    removeItemBool = True
    
    global itemToRemove
    itemToRemove = selectedDropMenuPath
    
    savePreferences()
    

"""
#----------------------------------------------------------------------------------------------------------------------
# EXPORT CHECKBOX SETTINGS
#----------------------------------------------------------------------------------------------------------------------
"""
#-------------
# OPTIMIZE SCENE OPTIONS MENU
#-------------
def optimizeSceneOptions(*args):
    mel.eval('OptimizeSceneOptions')

#-------------
# HELP DIALOG_ IGNORE ASSETS SOURCE
#-------------
def helpDialog_ignoreAssetsSource(*args):
    cmds.confirmDialog(title="What is 'Ignore Assets_Source'?",
                       message='(Smart Export Only) - By default, with this option unchecked, this tool will check if your export path contains the term "/Assets_Source/" (case-sensitive). If found, the tool will export to this location. "Assets_Source" is meant for temporary and Work-In-Progress assets rather than production ready assets, allowing for further quality control.',
                        button=['Okay!'] )

#-------------
# HELP DIALOG_ SMART EXPORT
#-------------
def helpDialog_smartExport(*args):
        cmds.confirmDialog(title="What is 'Smart Export'?",
                       message='Smart Export is a One-Click-Export feature that will scan every Asset folder for a file with a matching naming convention to this open scene file, and when found, will export this scene to overwrite that file. The naming convention used is (assetName_xx.ma) where "assetName" is the file name, and where "_xx" denotes file version (eg: characterJoe_56.ma ). The exported file will be "characterJoe.ma" in this example, found in your appropriate asset folder. Do not use the same file name across multiple art assets, as any of these may be overwritten! ',
                        button=['Okay!'] )

#-------------
# TOGGLE HISTORY CHECKBOXES
#-------------
def toggleHistoryCB(hisType, *args):
     #cmds.checkBox('cb_delNonDeformerHistory', edit=True, value=False)

    if hisType is "1":
        if cmds.checkBox ('cb_deleteHistory', query=True, value=True):
            cmds.checkBox ('cb_delNonDeformerHistory', edit=True, value=False)

    if hisType is "2":
        if cmds.checkBox ('cb_delNonDeformerHistory', query=True, value=True):
            cmds.checkBox ('cb_deleteHistory', edit=True, value=False)

#-------------
# TOGGLE SMART EXPORT CHECKBOXES
#-------------
def smartExportToggle(*args):
    if cmds.checkBox('cb_smartExport', query=True, value=True):
        cmds.checkBox('cb_ignoreAssetsSource', edit=True, enable=True, value=False)
        cmds.button('help_ignoreAssetsSource', edit=True, enable=True)
        
    if not cmds.checkBox('cb_smartExport', query=True, value=True):
        cmds.checkBox('cb_ignoreAssetsSource', edit=True, enable=False, value=False)
        cmds.button('help_ignoreAssetsSource', edit=True, enable=False)
        

#-------------
# EXPORT SCENE
#-------------
def export(*args):
    global exportSave
    
    if not cmds.file ( query=True, sceneName=True, shortName=True ):
        cmds.confirmDialog(title="Scene Name Does Not Exist!",
                                message='You must first save your scene, and thus give this file a name!', button=['Okay!'] )
    else:
        smartExportBool = False
        
        global exploreFilePath
        
        newSceneFileName = ''
        
        mayaVersion = mel.eval('about -v')
        
        #Check for 32bit or 64bit install path and load our fbx plugin
        if os.path.exists( 'C:/Program Files (x86)/Autodesk/Maya' + str(mayaVersion) + '/bin/plug-ins/fbxmaya.mll' ):
            cmds.loadPlugin ( 'C:/Program Files (x86)/Autodesk/Maya' + str(mayaVersion) + '/bin/plug-ins/fbxmaya.mll' )
            
        elif os.path.exists( 'C:/Program Files/Autodesk/Maya' + str(mayaVersion) + '/bin/plug-ins/fbxmaya.mll' ):
            cmds.loadPlugin ( 'C:/Program Files/Autodesk/Maya' + str(mayaVersion) + '/bin/plug-ins/fbxmaya.mll' )
        else:
            print("Cannot find FBX plugin, manually enable it!")
        
        #optimize scene
        if cmds.checkBox ('cb_optimizeScene', query=True, value=True):
            mel.eval ('OptimizeScene')
            
        #freeze transforms
        if cmds.checkBox ('cb_freezeTransformations', query=True, value=True):
            mel.eval ('select -all -hi')
            mel.eval ('FreezeTransformations')
            mel.eval ('select -clear')
        
        #center pivots
        if cmds.checkBox ('cb_centerPivots', query=True, value=True):
            mel.eval ('select -all -hi')
            mel.eval ('CenterPivot')
            mel.eval ('select -clear')
        
        #delete history
        if cmds.checkBox ('cb_deleteHistory', query=True, value=True):
            mel.eval ('DeleteAllHistory')
        
        #delete non deformer history
        if cmds.checkBox ('cb_delNonDeformerHistory', query=True, value=True):
            mel.eval ('BakeAllNonDefHistory')
        
        #save scene
        if cmds.checkBox ('cb_saveScene', query=True, value=True) or smartExportBool is True:
            #Query our current file name and path
            currentSceneFileName = cmds.file ( query=True, sceneName=True )
            extensionlessCurrentSceneFileName = currentSceneFileName[:-3]
            
            if cmds.checkBox ('cb_saveScene', query=True, value=True):
                #Use a regular expression to check for \d (digits) at the end of a string (+$)
                m = re.search(r'\d+$', extensionlessCurrentSceneFileName)
                
                if m is not None:
                    #we have a 'm'atch! So lets remove the numbers from our file name....
                    tempM = str ( m.group() )
                    numToStrip = str ( extensionlessCurrentSceneFileName ).rindex(tempM)
                    stripedFileVerCurrentSceneFileName = extensionlessCurrentSceneFileName[:numToStrip]
                    #Then we convert it from string to an int and increment the version of our file
                    fileVer = int( tempM )
                    fileVer += 1
                    #If our file ver is less than two digits, then we can prefix an extra "0" beforehand (eg: file_02.ma)
                    if len( str( fileVer ) ) << 2:
                        newSceneFileName = stripedFileVerCurrentSceneFileName + "0" + str(fileVer) + ".ma"
                        cmds.file( newSceneFileName, type="mayaAscii", exportAll=True )
                    #Otherwise, only suffix the file extension
                    if len( str( fileVer ) ) >= 2:
                        newSceneFileName = stripedFileVerCurrentSceneFileName + str(fileVer) + ".ma"
                        cmds.file( newSceneFileName, type="mayaAscii", exportAll=True )
                        
                if m is None:
                    newSceneFileName = extensionlessCurrentSceneFileName + "_01" + ".ma"
                    cmds.file( newSceneFileName, type="mayaAscii", exportAll=True )
                
        #ignore asset source
        ignoreAssetsSource = False
        
        if cmds.checkBox ('cb_ignoreAssetsSource', query=True, value=True):
            ignoreAssetsSource = True
        
        #smart export
        if cmds.checkBox ('cb_smartExport', query=True, value=True):
            smartExportBool = True

        purifyStr = str(selectedDropMenuPath)
        purifiedStr = purifyStr.index(":")-1
        toOpen = str(purifyStr)[purifiedStr:]
        
        exported=False
        
        #------
        #MANUAL EXPORT
        #------

        if smartExportBool is False:

            ff = "Maya ASCII (*.ma);; Autodesk FBX (*.fbx);; Wavefront OBJ (*.obj);; All Files (*.*)"
            saveAsFile = cmds.fileDialog2(caption="Export to...", dialogStyle=2, fileMode= 0, fileFilter=ff,
                                           startingDirectory=str(toOpen), returnFilter=True )

            #Find the last character '\' and remove everything from that point and before, returning only the file name
            purSaveAsFile = str(saveAsFile[0]).rindex("/")+1
            fileNameToSaveAs = str( saveAsFile[0] )[purSaveAsFile:]
            manualExportFilePath = str( saveAsFile[0] )
            
            #Find the last character '\' and remove everything from that point onwards, only returning the folder path we saved to
            #This is for texture exporting
            textureManualExportPath = str( saveAsFile[0] )[:purSaveAsFile]
            
            #File path to explore to
            exploreFilePath = str(saveAsFile[0] )[:purSaveAsFile]
            
            if exploreFilePath:
                cmds.iconTextButton('exploreFilePathBtn', style="iconAndTextVertical", edit=True, image="fileOpen.xpm", label="Explore",
                                     width=60, command=exploreSavedItem, visible=True )

            #Our File Type to save as
            if manualExportFilePath.endswith(".fbx"):
                manualExportFileType = "FBX export"

            if manualExportFilePath.endswith(".obj"):
                manualExportFileType = "OBJexport"

            if manualExportFilePath.endswith(".ma"):
                manualExportFileType = "mayaAscii"

            #set our file name selection button to be the name we've selected
            cmds.button('exportBtn', edit=True, label=str(fileNameToSaveAs)+"\n EXPORTED!",
                         backgroundColor=(0.1,0.1,0.1), height=60, command=export)
            
            #Finally export our file
            cmds.file( str(manualExportFilePath), type=manualExportFileType, exportAll=True )
            exported=True
            
        #------
        #SMART, AUTOMATIC ONE-CLICK EXPORT
        #------
        if smartExportBool is True:
            
            #Our current scene name
            currentSceneFileName = cmds.file ( query=True, shortName=True, sceneName=True )
            seCurrentSceneName = (currentSceneFileName)

            #Remove our file extension from our scene name
            purSceneName = seCurrentSceneName[:-3]        
            truncatedSceneName = purSceneName
            
            #Use a regular expression to check for \d (digits) at the end of a string (+$)
            m2 = re.search(r'\d+$', purSceneName)

            if m2 is not None:
                #we have a 'm'atch! So lets remove the numbers from our file name....
                tempM2 = int ( len ( str ( m2.group() ) ) )
                apurSceneName = purSceneName[:-tempM2]
            
                if apurSceneName.endswith("_"):
                    truncatedSceneName = apurSceneName[:-1]
            
            if m2 is None:
                if purSceneName.endswith("_"):
                        truncatedSceneName = apurSceneName[:-1]
            
            #Our selected project file path from our dropDownMenu is our directory to scan
            directory = toOpen
            smartExportFileType = 'mayaAscii'
            
            if ignoreAssetsSource is True:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        #regular expression to search through our current directory path for "Assets_Source"
                        m3 = re.search("Assets_Source", raw_string(root))

                        #if assetSourceMatch != "Assets_Source":
                        if m3 is None:
                            if file.startswith(truncatedSceneName):
                                
                                if file.endswith(".fbx"):
                                    smartExportFileType = "FBX export"
                                
                                if file.endswith(".obj"):
                                    smartExportFileType = "OBJexport"
                                    
                                if file.endswith(".ma"):
                                    smartExportFileType = "mayaAscii"
                                
                                smartExportSaveTo = str(root) + "/" + truncatedSceneName
                                smartExportFilePath = str(root) + "/"
                                cmds.file( str(smartExportSaveTo), type=smartExportFileType, exportAll=True )
                                exported=True
                            
            
            if ignoreAssetsSource is False:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        #regular expression to search through our current directory path for "Assets_Source"
                        m3 = re.search("Assets_Source", raw_string(root))
                        
                        if m3 is not None:
                            assetSourceMatch = str(m3.group())
                            if assetSourceMatch == "Assets_Source":
                                m4 = re.search(str(truncatedSceneName), str(file))
                                
                                if m4 is not None:
                                    if file.endswith(".fbx"):
                                        smartExportFileType = "FBX export"
                                    
                                    if file.endswith(".obj"):
                                        smartExportFileType = "OBJexport"
                                        
                                    if file.endswith(".ma"):
                                        smartExportFileType = "mayaAscii"
                                    
                                    smartExportSaveTo = str(root) + "/" + truncatedSceneName
                                    smartExportFilePath = str(root) + "/"
                                    cmds.file( str(smartExportSaveTo), type=smartExportFileType, exportAll=True )
                                    exported=True
                
            #File path to explore to
            if exported is True:
                exploreFilePath = str( smartExportFilePath )
                
                if exploreFilePath:
                    cmds.iconTextButton('exploreFilePathBtn', style="iconAndTextVertical",
                                         edit=True, image="fileOpen.xpm", label="Explore",
                                         width=60, command=exploreSavedItem, visible=True )

                #our SaveScene option must now open its new file
                if newSceneFileName:
                    cmds.file( str(newSceneFileName), open=True, force=True )
            
            if exported is False:
                cmds.confirmDialog(title="Could Not Export!", 
                               message="Could Not Export! - Either the file to find doesn't exist or your naming convention with this scene file is incorrect. Double check the naming conventions under 'What is this?' help button from the 'Smart Export' checkbox. Otherwise, Manually Export this file first then use 'Smart Export'.", button=['Okay!'] )
            
        #------
        #EXPORT TEXTURES
        #------
        if cmds.checkBox ('cb_exportTextures', query=True, value=True):
            
            #delete unused nodes
            mel.eval(' hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes") ')
            
            #query our texture files
            fileTextureList = cmds.ls(textures=True)
            
            #export Our Textures
            for fileName in fileTextureList:
                texturePath = cmds.getAttr(fileName+".fileTextureName")
                
                #Works with Manual export
                if smartExportBool is False:
                    shutil.copy2(texturePath, textureManualExportPath)

                #Works with Smart Export
                if smartExportBool is True:
                    shutil.copy2(texturePath, smartExportFilePath)
                    
                    
        #SAVE export settings
        exportSave = True
        savePreferences()
    

"""
#----------------------------------------------------------------------------------------------------------------------
# CREATE OUR MENU
#----------------------------------------------------------------------------------------------------------------------
"""
# Create our interface
def createGUI_km2uet():
    global maxRange
    global loadedProjNameFolderListLength
    global selectedDropMenuPath
    global removeItemBool
    removeItemBool = False
    
    #Our default drop-down Menu Item
    global defaultMenuItem
    defaultMenuItem = None
    
    #loadPreferences
    loadPreferences()
    
    #check for existing window first, and if exists, delete it for recreation
    if cmds.window("kkMayaToUnityExporter", exists=True):
        cmds.deleteUI("kkMayaToUnityExporter")
    
    #create the window
    cmds.window("kkMayaToUnityExporter", title="Maya-2-Unity Exporter", wh=(350, 500), sizeable=False)
    
    #create base layout
    cmds.columnLayout( adjustableColumn=True ) #essentially allows for our collapsable frameLayouts!!!
    
    #-------------
    # LAYOUT CREATION_  ADD PROJECT FOLDERS
    #-------------
    
    cmds.frameLayout( label="Add a Project Folder", labelVisible=True, collapsable=True)
    cmds.separator(h=1, style="none")
    cmds.rowColumnLayout( numberOfColumns=3, rowSpacing=(1,5), columnOffset=(1,"left",5) )

    #Project Name text field
    cmds.text( label=' Project Name: ' )
    nameField = cmds.textField('projectNameTextField')
    cmds.textField( 'projectNameTextField', edit=True, height=25, width=250, text='')
    
    cmds.separator(h=20, style="none")
    
    #file browser text field
    cmds.text( label=' Folder Path: ' )
    cmds.textField( 'fileBrowserTextField', editable=False, height=25, width=250, backgroundColor=(0.2,0.2,0.2), text=str(fileBrowserPath) )
    
    #open file browser and select our path
    cmds.iconTextButton( style="iconAndTextVertical", image="fileOpen.xpm", label="Find Folder", width=70, command=fileBrowser )
    
    cmds.separator(h=20, style="none")
    
    #save button
    cmds.button( label='[ Add Project Folder To Export Menu ]', backgroundColor=(0.2,0.2,0.2), height=25, command= savePreferences )
    
    cmds.setParent('..') #end rowColumnLayout
    cmds.separator(h=1, style="none")
    cmds.setParent('..') #end frameLayout
    
    #-------------
    # LAYOUT ENDED_  ADD PROJECT FOLDERS
    #-------------

    #-------------
    # LAYOUT CREATION_  CHECKBOX SETTINGS
    #-------------
    
    cmds.frameLayout( label="Export Settings", labelVisible=True, collapsable=True)
    cmds.separator(h=1, style="none")
    cmds.rowColumnLayout( numberOfColumns=2, rowSpacing=(1,5), columnOffset=(1,"left",41))
    
    #01
    cmds.checkBox('cb_optimizeScene', label='Optimize Scene' )
    cmds.button( label='[Options]', width=50, command=optimizeSceneOptions )
    #02
    cmds.checkBox('cb_freezeTransformations', label='Freeze Transformations')
    cmds.separator(h=20, style="none")
    #03
    cmds.checkBox('cb_centerPivots', label='Center Pivots')
    cmds.separator(h=20, style="none")
    #04
    cmds.checkBox('cb_deleteHistory', label='Delete History', changeCommand=lambda delHis:toggleHistoryCB ( "1" ) )
    cmds.checkBox('cb_delNonDeformerHistory', label='Del Non-Deformer History', changeCommand=lambda delndHis:toggleHistoryCB ( "2" ) )
    #05
    cmds.checkBox('cb_saveScene', label='Save Scene')
    cmds.text(label='(Appends FileName_Ver.ma)')
    #07
    cmds.checkBox('cb_exportTextures', label='Export Textures')
    cmds.text(label='(Also deletes unused Nodes)')
    #08
    cmds.checkBox('cb_smartExport', label='Smart Export', changeCommand=smartExportToggle)
    cmds.button('help_smartExport', label='What is this?', width=50, command=helpDialog_smartExport )
    #09
    cmds.checkBox('cb_ignoreAssetsSource', label='Ignore Assets_Source', enable=False)
    cmds.button('help_ignoreAssetsSource', label='What is this?', width=50, command=helpDialog_ignoreAssetsSource, enable=False)
                            
    #Load our checkbox settings
    for cbs_n in loadedcbsList:
        if cbs_n != '' and cbs_n is not None:
            if cmds.checkBox(cbs_n, query=True, exists=True):
                cmds.checkBox(cbs_n, edit=True, value=True)
                
                if cbs_n == "cb_smartExport":
                    cmds.checkBox('cb_ignoreAssetsSource', edit=True, value=True, enable=True)
                    cmds.button('help_ignoreAssetsSource', edit=True, enable=True)

    cmds.setParent('..') #end rowColumnLayout
    cmds.separator(h=1, style="none")
    cmds.setParent('..') #end frameLayout
    
    #-------------
    # LAYOUT ENDED_  CHECKBOX SETTINGS
    #-------------

    #-------------
    # LAYOUT CREATION_  SELECT PROJECT FOLDERS AND EXPORT
    #-------------
    
    cmds.frameLayout( label="Select Project To Export To", labelVisible=True, collapsable=True)
    cmds.separator(h=1, style="none")
    cmds.rowColumnLayout( numberOfColumns=4, rowSpacing=(10,10), columnOffset=(1,"left",5)) #1
        
    #create our drop-down menu to display our saved project paths from loadPreferences
    cmds.text( label='      Select:      ' )
    projectFolderMenu = cmds.optionMenu('dropDownMenu', height=30, width=255,backgroundColor=(0.2,0.2,0.2),
                                         changeCommand= lambda lambdaCC:selectedMenuItem ( str(lambdaCC)) )
    
    maxRange = loadedProjNameFolderListLength-1
    for i in range(0,loadedProjNameFolderListLength):
            cmds.menuItem('dropDownMenuField'+str(i), label=loadedProjNameFolderList[i], parent="dropDownMenu")
    
            #if we don't yet have a selection, such as on GUI creation, then the currently selected item should be the first (0)
            defaultMenuItem = str( mel.eval('menuItem -q -label dropDownMenuField'+str(0) ) )
            
            selectedDropMenuPath = defaultMenuItem
            
    #open selected project path folder, or remove it
    cmds.iconTextButton( style="iconAndTextVertical", image="fileOpen.xpm", label="Explore", width=50, command=exploreItem )
    cmds.iconTextButton( style="iconAndTextVertical", image="Mute_ON.png", label="Remove",
                         backgroundColor=(0.2,0.2,0.2), width=50, command=removeItem ) 
    
    cmds.setParent('..') #end rowColumnLayout 1
    
    cmds.rowColumnLayout( numberOfColumns=3, rowSpacing=(10,10), columnOffset=(1,"left",5)) #rowColumnLayout 2
    cmds.separator(h=20,w=70, style="none")
    
    #Export button
    cmds.button('exportBtn', label="[ EXPORT ] \n Manual Export + Smart Export", backgroundColor=(0.1,0.1,0.1),
                 height=60, width=250, command=export)
    cmds.iconTextButton('exploreFilePathBtn', style="iconAndTextVertical", image="fileOpen.xpm", label="Explore",
                         width=60, command=exploreSavedItem, visible=False )

    cmds.setParent('..') #end rowColumnLayout 2
    cmds.separator(h=1, style="none")
    cmds.setParent('..') #end frameLayout
    
    #-------------
    # LAYOUT ENDED_  SELECT PROJECT FOLDERS & Export
    #-------------
    
    cmds.setParent('..') #end columnLayout (base layout)
    
    #Finally, show the window
    cmds.showWindow("kkMayaToUnityExporter")

createGUI_km2uet()