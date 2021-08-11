"""

For Windows OS, Python 2.6, Maya 2022

-----------------------------------------------------------------------------------

The MIT License

Copyright (c) 2013 Kai Krause <kaikrause95@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import maya.cmds as cmds
import maya.mel as mel

#variables to access current slider values
tumbleScale = mel.eval('tumbleCtx -q -tumbleScale tumbleContext;')
dollyScale = mel.eval('dollyCtx -q -scale dollyContext;')
trackScale = mel.eval('trackCtx -q -trackScale trackContext;')

syncScale = 1.0;

camCOIVal = cmds.getAttr ("perspShape.centerOfInterest");

#apply slider values to camera settings
def TumbleUpdate(tumbleScale):
	mel.eval('tumbleCtx -e -tumbleScale ' +str(tumbleScale)+ ' tumbleContext;')

def DollyUpdate(dollyScale):
	mel.eval('dollyCtx -e -scale ' +str(dollyScale)+ ' dollyContext;')

def TrackUpdate(trackScale):
	mel.eval('trackCtx -e -trackScale ' +str(trackScale)+ ' trackContext;')

def SyncUpdate(syncScale):
	#apply slider values to camera settings
	mel.eval('tumbleCtx -e -tumbleScale ' +str(syncScale)+ ' tumbleContext;')
	mel.eval('dollyCtx -e -scale ' +str(syncScale)+ ' dollyContext;')
	mel.eval('trackCtx -e -trackScale ' +str(syncScale)+ ' trackContext;')

	#apply universal value to all sliders in GUI
	mel.eval('floatSliderGrp -e -v ' +str(syncScale)+ ' tumble;')
	mel.eval('floatSliderGrp -e -v ' +str(syncScale)+ ' dolly;')
	mel.eval('floatSliderGrp -e -v ' +str(syncScale)+ ' track;')

def ResetToDefault(*args):
	syncScale = 1.0
	mel.eval('floatSliderGrp -e -v ' +str(syncScale)+ ' sync;')
	SyncUpdate(syncScale)

#Initiate interface
def createGUI_cms():
	#check for existing window first
	if cmds.window("camMovScale", exists=True):
		cmds.deleteUI("camMovScale")

	#create the window
	cmds.window("camMovScale", title="Camera Movement Scale", wh=(255, 210), sizeable=False)

	#create layout
	cmds.frameLayout(marginHeight=3, marginWidth=3, labelVisible=False)
	cmds.columnLayout()

	#create Tumble field with slider
	cmds.text(label="Tumble (Camera Rotate) Scale")
	cmds.floatSliderGrp ('tumble', field=True, minValue=0.0000, maxValue=10.0000, fieldMinValue=-0.0000, fieldMaxValue=10.0000, value=tumbleScale, precision=4, changeCommand= TumbleUpdate)
	cmds.separator(h=10, style="none")

	#create Dolly field with slider
	cmds.text(label="Dolly (Camera Zoom) Scale")
	cmds.floatSliderGrp('dolly', field=True, minValue=0.0000, maxValue=10.0000, fieldMinValue=-0.0000, fieldMaxValue=10.0000, value=dollyScale, precision=4, changeCommand= DollyUpdate )
	cmds.separator(h=10, style="none")

	#create Track field with slider
	cmds.text(label="Track (Camera Pan) Scale")
	cmds.floatSliderGrp('track', field=True, minValue=0.0000, maxValue=10.0000, fieldMinValue=-0.0000, fieldMaxValue=10.0000, value=trackScale, precision=4, changeCommand= TrackUpdate )
	cmds.separator(h=10, style="none")

	#create Sync field with slider
	cmds.text(label="Sync All")
	cmds.floatSliderGrp('sync', field=True, minValue=0.0000, maxValue=10.0000, fieldMinValue=-0.0000, fieldMaxValue=10.0000, value=syncScale, precision=4, bgc=(0.4,0.4,0.4), changeCommand= SyncUpdate)
	cmds.separator(h=10, style="none")

	#create button to reset all fields to their default values
	cmds.button( label='Reset to default', width=248, command= ResetToDefault )

	cmds.setParent('..') #end rowLayout

	#finally, show the window
	cmds.showWindow("camMovScale")

createGUI_cms()
