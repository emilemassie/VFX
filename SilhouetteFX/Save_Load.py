import fx, os
from Qt import *



def checkENV():
	try:
		if os.environ['PXO_TASK_ROOT']:
			SessionPath = os.path.join(os.path.expandvars("$PXO_TASK_ROOT"), 'SilhouetteScripts')
			return True
	except:
			fx.displayInformation('Cannot find environement variables \nPlease make sure your Project/Sequence/Shot and Task are set correctly.', title="Can't find ENV !!!")
			return False


def ImportPlate():
	
	"""OPEN A DIALOG WINDOW FOR THE ARTIST TO SELECT THE PLATE THEY WANT TO WORK ON AND IMPORT THE SOURCEPLATE INTO THE PROJECT."""
	
	PlatePath = os.path.join(
			os.path.expandvars("$PXO_ELEMENTS_ROOT"),
			os.path.expandvars('$PXO_PROJECT'),
			os.path.expandvars('$PXO_SEQUENCE'),
			os.path.expandvars('$PXO_SHOT'),
			'elements', 'plates'
	)

	dialog = QtWidgets.QFileDialog(caption = 'PLEASE SELECT THE PLATE YOU WANT TO WORK ON')
	dialog.setDirectory(PlatePath)

	if dialog.exec_():
		#Defining variables to be used in the path creation
		filename = dialog.selectedFiles()[0]
		prefix = filename.split('.')[-3]
		dirpath = os.path.dirname(os.path.os.path.realpath(filename))
		basename = os.path.basename(filename).split('.')[0]
		images = [img for img in os.listdir(dirpath) if img.startswith(basename) and img.endswith(filename.split('.')[-1])]

		#Silhouette only takes sequences as myfile.[1001-1100].exr
		#So lets build the path according to the user selection
		importFileName = prefix+'.['+ str(images[0].split('.')[-2])+'-'+str(images[-1].split('.')[-2])+'].'+ filename.split('.')[-1]
		saveSessionName = basename.split('_v')[0]
		

		#import the plate into the project
		source = fx.Source(path=importFileName)

		pathFromSelectedPlate = os.path.join(os.path.expandvars("$PXO_TASK_ROOT"),'SilhouetteScripts',saveSessionName)+'_'+os.path.expandvars('$PXO_TASK')+'_' + os.path.expandvars('$PXO_USER_ABBR')+'_v001'
		
		p = fx.Project(pathFromSelectedPlate)
		fx.activate(p)
		fx.activeProject().addItem(source)
		
		return pathFromSelectedPlate

class SaveGUI(QtWidgets.QDialog):
	def __init__(self, parent=None):
		"""Creates the GUI window for the user to give them options to chose from."""
		
		super(SaveGUI, self).__init__(parent)

		self.SessionPath = os.path.join(os.path.expandvars("$PXO_TASK_ROOT"), 'SilhouetteScripts')

		self.setMinimumSize(600, 400)
		self.setWindowTitle("SAVE/LOAD")
		self.setModal(True)
		
		self.layout = QtWidgets.QVBoxLayout()
		self.hlayout = QtWidgets.QHBoxLayout()		
		self.setStyleSheet('background-color:#00000')
		

		#self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

		self.CommentText = QtWidgets.QPlainTextEdit()
		self.CommentText.setPlaceholderText('--- Insert comments in here ---')
		self.SaveButton = QtWidgets.QPushButton("SAVE NEW VERSION")

		self.choice = QtWidgets.QComboBox()
		self.choice.insertItems(0, self.buildList())
		self.choice.setCurrentIndex(self.choice.count()-1)
		self.choice.currentIndexChanged.connect(self.UpdateUI)
		self.choice.currentTextChanged.connect(self.UpdateUI)
		self.choice.setEditable(True)
		self.layout.addWidget(self.choice)


		
		self.layout.addWidget(self.CommentText)

		self.SaveButton.setStyleSheet('background-color: #320A50;padding:8')
		self.hlayout.addWidget(self.SaveButton)
		self.SaveButton.clicked.connect(self.buttonPressed)

		self.cancelbutton = QtWidgets.QPushButton("CANCEL")
		self.hlayout.addWidget(self.cancelbutton)
		self.cancelbutton.clicked.connect(self.reject)
		self.cancelbutton.setStyleSheet('padding:8')


		self.layout.addLayout(self.hlayout)
		self.setLayout(self.layout)
		self.UpdateUI()


	def buildList(self):

		if os.path.isdir(self.SessionPath):
			self.list = os.listdir(self.SessionPath)
			try:
				self.list.remove('_deadline_projects')
			except:
				self.list = os.listdir(self.SessionPath)
			try:
				fx.activeProject().path
				self.list.append(self.list[-1].split('.')[0].split('_v')[0]+'_v'+str(int(self.list[-1].split('.')[0].split('_v')[-1])+1).zfill(3)+'.sfx')
			except:
				self.SaveButton.setText('LOAD LATEST VERSION')
			return self.list
		else:
			self.CommentText.setPlainText('First build using the assistant : \n----------------------------------------\n\n\n')
			return ['Session Builder Assistant']

	def buttonPressed(self):

		if self.SaveButton.text() == 'SAVE NEW VERSION':
			self.SaveScript()
		elif self.SaveButton.text() == 'SAVE CUSTOM NAME':
			fx.activate(fx.Project(os.path.join(self.SessionPath, self.choice.currentText().split('.sfx')[0])))
			self.SaveScript()
		else :
			self.LoadScript()

	def SaveScript(self):

		if self.choice.currentText() == 'Session Builder Assistant':
			ImportPlate()
			fx.activeProject().save()
			with open(os.path.join(fx.activeProject().path.rsplit('/',1)[0],'VersionNote.txt'),'w+') as f:
				f.write(self.CommentText.toPlainText())
		else:
			fx.activeProject().save(path=os.path.join(self.SessionPath, self.choice.currentText().split('.sfx')[0]))
			with open(os.path.join(self.SessionPath, self.choice.currentText(), 'VersionNote.txt'),'w+') as f:
				f.write(self.CommentText.toPlainText())
		self.accept()

	def LoadScript(self):
		fx.loadProject(os.path.join(self.SessionPath, self.choice.currentText()))
		self.accept()

	def UpdateUI(self):
		if self.choice.currentIndex() == self.choice.count()-1:
			try: 
				fx.activeProject().path
				self.SaveButton.setText('SAVE NEW VERSION')
				self.CommentText.setPlaceholderText('--- Insert comments in here ---')
			except:
				self.list = self.buildList()
				if self.choice.currentText() != self.list[-1]:
					 self.SaveButton.setText('SAVE CUSTOM NAME')
				else:
					#self.SaveButton.setText('LOAD LATEST VERSION')
					try:
						with open(os.path.join(self.SessionPath, self.choice.currentText(), 'VersionNote.txt')) as f:
							self.CommentText.setPlaceholderText(f.read())
					except:
						self.CommentText.setPlaceholderText('Cannot find comments for this version')
		else :
			versionName = self.choice.currentText().split('_')[-1].split('.')[0]
			self.SaveButton.setText('LOAD : ' + versionName)
			try:
				with open(os.path.join(self.SessionPath, self.choice.currentText(), 'VersionNote.txt')) as f:
					self.CommentText.setPlaceholderText(f.read())
			except:
				self.CommentText.setPlaceholderText('Cannot find comments for this version')
			
			
def showSaveLoad():
	SaveWindow = SaveGUI()
	SaveWindow.exec()

class OpenSaveLoad(fx.Action):
	"""Creates the action for silhouette to be able to call it later."""

	def __init__(self):
		fx.Action.__init__(self, "PXO|Save/Load (Ctrl+Alt+S)")
	def execute(self):
		if checkENV():
			showSaveLoad()
			fx.activeProject().save()

fx.addAction(OpenSaveLoad())
fx.bind("Ctrl+Alt+o", showSaveLoad)
fx.bind("Ctrl+Alt+s", showSaveLoad)



#LEAVING THIS HERE TO OPEN THE WINDOW NO MATTER WHAT

if (fx.gui):
	showSaveLoad()