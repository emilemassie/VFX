import fx, os, tempfile, time
from fx import *



def applyCornerPin(cpindata):
	node = activeNode()
	session = node.session
#	rotoNode = session.node(type="RotoNode")
	to1 = Tracker("cpin_to1")
	to2 = Tracker("cpin_to2")
	to3 = Tracker("cpin_to3")
	to4 = Tracker("cpin_to4")	
	trackers = [to1,to2,to3,to4]
	node.property("objects").addObjects([to1])
	node.property("objects").addObjects([to2])
	node.property("objects").addObjects([to3])
	node.property("objects").addObjects([to4])
	
	for item in cpindata:
		time1 = item[0] - session.startFrame
		n = 1
		for trk in trackers:
			position = trk.property("position")
			position.constant = False
			pEditor = PropertyEditor(position)
 			#==================================================================
 			# Height on Silhouette = session.height - Nuke height
 			# Mapping from silhouette coordinate to pixel coordinates:
 			# Value - half of the width/height / height session
 			#==================================================================
			x = ((item[n] - (session.size[0]/2))/session.size[1])* session.pixelAspect
			y = ((session.size[1]-item[n+1]) - (session.size[1]/2))/session.size[1]
			pEditor.setValue(Point3D(x,y,0),time1)
			n+=2
			pEditor.execute()
	
	firstframe = cpindata[0][0]
	if firstframe != session.startFrame:
		for trk in trackers:
			position = trk.property("position")	
			pEditor = PropertyEditor(position)
			pEditor.deleteKey(0)
			pEditor.execute()
	print("Corner Pin Imported successfully", time.strftime("%a, %d %b %Y %H:%M:%Sgmt", time.gmtime()))

def verifyClipboard(clipboard):
	if "CornerPin2D {" in clipboard and "curve" in clipboard: #"curve" identify animated trackers
		fx.status("Nuke Corner Pin detected on Clipboard: Importing...")
		itens = clipboard.split("curve ") #gets each sequence of to"n" values, to1, to2, to3, to4
		valueList = []
		#=======================================================================
		# build the frames index
		# handles data coming from mocha and nuke "cut_paste"
		#=======================================================================
		subitem = itens[1].split("}")
		subitem = subitem[0].split()
		x=0
		while x < len(subitem):#
			if subitem[x].count("x") > 0:
				frame = subitem[x][1:]
				valueList.append([int(frame)])
				lastx = x
			else:
				if (x - lastx) > 1:
					valueList.append([int(subitem[lastx][1:]) + (x-lastx-1)])
			x+=1

		#=======================================================================
		# add to"n" values for the frames, format: [frame, to1x, to1y, to2x, to2y, to3x, to3y, to4x, to4y]
		#=======================================================================
		for i in range(1, len(itens)):
			subitem = itens[i].split("}")
			subitem = subitem[0].split()
			x = 1
			n = 0
			while x < len(subitem):#	
				if subitem[x].count("x") == 0:
					value = subitem[x]
					valueList[n].append(float(value))
					n+=1
				x+=1
		return valueList	
	else:
		return False


def importFromClipboard():
	fx.beginUndo('Import Clipboard Tracks')

	from Qt import QtWidgets
	clipboard = QtWidgets.QApplication.clipboard()
	tempFile = "{0}/ClipboardTrackerImport.nk".format(tempfile.gettempdir())
	cornerpin = clipboard.text()
	print(cornerpin)
	
	checkClipboard = verifyClipboard(cornerpin)
	if not checkClipboard:
		fx.status("No valid clipboard data detected, aborting script.")
		print( "No valid clipboard data detected, aborting script.", time.strftime("%a, %d %b %Y %H:%M:%Sgmt", time.gmtime()))
	else:
		applyCornerPin(checkClipboard)	
	endUndo()

class ImportTrackFromClipboard(fx.Action):
	"""Creates the action for silhouette to be able to call it later."""
	def __init__(self):
		fx.Action.__init__(self, "PXO|Import CornerPin from Clipboard (Ctrl+Alt+V)")
	def execute(self):
		importFromClipboard()

fx.addAction(ImportTrackFromClipboard())
fx.bind("Ctrl+Alt+v", importFromClipboard)
