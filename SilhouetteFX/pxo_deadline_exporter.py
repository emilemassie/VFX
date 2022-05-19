# Import built-in modules
from datetime import datetime
import os
import subprocess

# Import third-party modules
from Qt import QtWidgets
import fx

deadlineExe = "C:\\Program Files\\Thinkbox\\Deadline8\\bin\\deadlinecommand.exe"
silhouetteExe = os.path.join(
    os.path.expandvars("$REZ_SILHOUETTEFX_ROOT").replace(
        "C:\\_pxo\\rez_local_cache\\ext", os.path.expandvars("$PXO_EXT")
    ),
    "sfxcmd.exe",
)


def statusUpdate(txt):
    """Prints the status in the silhouette UI (bottom bar) and the console for debuging."""
    fx.status(str(txt))
    print(str(txt))


def RemoveBadOutputs():
    """removes all the output nodes in the active session."""
    for node in fx.activeSession().nodes:
        if node.isType("OutputNode"):
            fx.activeSession().removeNode(node)


def getProjectName():
    """Return the active project name."""
    if fx.activeProject():
        return os.path.basename(os.path.dirname(fx.activeProject().path)).replace(
            ".sfx", ""
        )
    return ""


class GUI(QtWidgets.QDialog):
    def __init__(self, parent=None):

        """Creates the GUI window for the user to give them options to chose from."""

        self.deadlineProjectPath = ""

        self.ICON_String = """
$@@@@@@@@@@@@@@       B@@@@      ,@@@@@@@@@@@gg   
$@@@@@NNNNNBB@@@W      %@C      g@@@@@NNB@@@@@@@g 
$@@@@@       ]@@@@g     `     g@@@@'      ]$@@@@@g
$@@@@@       g@@@@@P        ,@@@@@          @@@@@@
$@@@@@@@@@@@@@@@@@P         ]@@@@@          @@@@@@
@@@@@@BBBBBBBBBN*`            %@@@         ]@@@@@@
@@@@@@                 ,@      "B@@g,    ,g@@@@@@"
@@@@@@                g@@@p      "@@@@@@@@@@@@@P  
NNNNNN               4NNNNNN       %NNNNNNNP""    
"""

        super(GUI, self).__init__(parent)
        self.setWindowTitle("Deadline Exporter")
        self.setModal(True)

        self.form = QtWidgets.QFormLayout()
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.ICON = QtWidgets.QLabel(self.ICON_String)
        self.ICON.setStyleSheet(
            "QLabel{font-size: 10px;font-family: Courier New;padding: auto;}"
        )
        self.form.addRow(self.ICON)

        self.type = QtWidgets.QComboBox()
        self.type.insertItems(0, ["ROTO", "PAINT"])
        self.type.currentIndexChanged.connect(self.getNodes)
        self.form.addRow("<b>TASK TYPE : ", self.type)

        self.node = QtWidgets.QComboBox()
        self.node.insertItems(0, self.initnodes())
        self.form.addRow("<b>NODE TO RENDER : ", self.node)

        self.chunksize = QtWidgets.QSpinBox()
        self.chunksize.setMinimum(1)
        self.chunksize.setMaximum(999)
        self.chunksize.setValue(20)
        self.form.addRow("<b>BATCH SIZE : ", self.chunksize)

        self.sendCHKBox = QtWidgets.QCheckBox("*Will not submit the render to deadline")
        self.form.addRow("<b>SKIP RENDER", self.sendCHKBox)

        self.LocalCHKBox = QtWidgets.QCheckBox("*Render localy on this machine")
        self.form.addRow("<b>RENDER LOCAL", self.LocalCHKBox)

        self.hintText = QtWidgets.QLabel(
            "<br><br><b>ROTO : </b>Will grab the top layers of the given node and render a MultilayerEXR.<br><b>PAINT : </b>Will plug the output node into the given node and render RGBA (strokes)<br><br>"
        )
        self.hintText.setStyleSheet("QLabel{font-size: 10px;}")
        self.form.addRow(self.hintText)

        self.layout.addLayout(self.form)
        self.sendbutton = QtWidgets.QPushButton("SEND")
        self.layout.addWidget(self.sendbutton)

        self.cancelbutton = QtWidgets.QPushButton("CANCEL")
        self.layout.addWidget(self.cancelbutton)

        self.sendbutton.clicked.connect(self.PackAndSend)
        self.cancelbutton.clicked.connect(self.reject)

        self.setLayout(self.layout)

    def getNodes(self, index):
        """This function is called to update the content of the node drop down menu.
        it will add the good type of node to the list according to the task type previously selected."""

        self.node.clear()
        list = []
        if index == 0:
            for i in fx.activeSession().nodes:
                if i.isType("RotoNode"):
                    list.append(i.label)
        if index == 1:
            for i in fx.activeSession().nodes:
                list.append(i.label)
        self.node.insertItems(0, list)

    def initnodes(self):
        rotoList = []
        for i in fx.activeSession().nodes:
            if i.isType("RotoNode"):
                rotoList.append(i.label)
        return rotoList

    def SetAndBackupSession(self):
        """CREATE THE DEADLINE SESSION AND RESTORE THE ORIGINAL ONE"""
        OG_PATH = fx.activeProject().path

        timeID = datetime.now().strftime("%d%m%Y%H%M%S")
        self.deadlineProjectPath = ""

        if fx.activeProject():
            self.deadlineProjectPath = os.path.join(
                os.path.dirname(os.path.dirname(fx.activeProject().path)),
                "_deadline_projects",
                str(timeID),
            ).replace("\\", "/")

        fx.activeProject().save(path=self.deadlineProjectPath)
        fx.loadProject(OG_PATH)

    def PackAndSend(self):
        self.OG_SESSION = fx.activeSession().clone()
        if self.type.currentText() == "ROTO":
            fx.activeProject().save()
            self.PkgRoto(self.node.currentText())
            self.SetAndBackupSession()
        if self.type.currentText() == "PAINT":
            fx.activeProject().save()
            self.PkgPaint(self.node.currentText())
            self.SetAndBackupSession()
        if self.SendSessionToDeadline():
            self.accept()
            #fx.displayInformation(
            #    '<center style="font: 12px">SENT TO DEADLINE !!!\n\n\n</center>',
            #    title="SUCCESS !!!",
            #)

    def SendSessionToDeadline(self):
        """Builds and execute the command to send the session to deadline"""

        frame_range = (
            str(int(fx.activeSession().workRange[0]))
            + "-"
            + str(int(fx.activeSession().workRange[1]))
        )
        scriptpath = self.deadlineProjectPath + ".sfx"

        name = (
            '"SilhouetteFX ---> '
            + str(fx.activeProject()).split("/")[-1]
            + " ["
            + frame_range
            + ']"'
        )
        arguments = (
            silhouetteExe + " -range " + "<STARTFRAME>-<ENDFRAME>" + " " + scriptpath
        )

        fullcommand = (
            deadlineExe
            + " -SubmitCommandLineJob -executable "
            + '"{0}"'.format(os.path.join(os.path.expandvars("$PXO_ROOT"), "pxo.cmd"))
            + " -name " + name
            + " -frames " + frame_range
            + " -chunksize " + str(self.chunksize.value())
            + ' -prop ConcurrentTasks=2'
            + ' -Priority 80 -Group all -Pool comp -Department "Paint and roto" -arguments "+p silhouettefx_license run '
            + arguments
            + '"'
        )

        # SEND THE FULL COMMAND TO DEADLINE SUBMISSION
        print("SENDING " + frame_range + " with command:")
        print(fullcommand + "\n")

        if self.LocalCHKBox.isChecked(): # If its a local render
            LocalCommand = (
                silhouetteExe
                + ' -range ' + frame_range + ' ' 
                + scriptpath)

            subprocess.Popen(LocalCommand)
        else:
            if self.sendCHKBox.isChecked() == False:
                subprocess.Popen(fullcommand)
    
        return True

    def PkgRoto(self, nodename):
        """Modify the active session for exporting a roto task through Deadline. This functions will alter the active session and add the proper node to render in a multilayer EXR for roto delivery"""
        OG_ROTO_NODE = fx.activeSession().node(nodename)
        LAYER_LIST = []

        # CHECK IF PROJECT ALREADY CONTAINS A DEADLINE_RENDER Session
        for session in fx.activeProject().sessions:
            if session.label == "DEADLINE_RENDER":
                fx.activeProject().removeItem(session)

        ## GET PROPER PATH
        output_file = os.path.join(
            os.getenv("PXO_FRAMESTORE_ROOT"),
            os.getenv("PXO_PROJECT"),
            os.getenv("PXO_SEQUENCE"),
            os.getenv("PXO_SHOT"),
            "elements/2d/roto/silhouette_mattes",
            getProjectName(),
        ).replace("\\", "/")

        # ADD OUTPUT NODE
        RemoveBadOutputs()
        output_node = fx.Node("OutputMultiPartNode", label="DEADLINE_RENDER_NODE")
        output_node.setState("graph.pos", fx.Point3D(0, 300))
        output_node.properties["path"].value = output_file
        output_node.properties["channels"].value = 2
        output_node.properties["views"].value = 1
        fx.activeSession().addNode(output_node)

        OG_ROTO_NODE.port("output").connect(output_node.port("input"))

        # GET ALL THE TOP LAYER AND PUT IT IN ONE LIST
        for i in OG_ROTO_NODE.children:
            if i.isType("Layer"):
                LAYER_LIST.append(i)
                i.visible = False

        # CREATE A ROTO NODE WITH ONLY ONE LAYER AVAILIBLE AND CONNECT IT TO THE MULTI-OUTPUT
        for index, layer in enumerate(LAYER_LIST):
            layer.visible = True
            statusUpdate("Exporting layer : " + layer.label)
            newroto = OG_ROTO_NODE.clone()
            newroto.label = str(layer.label)
            newroto.setState("graph.pos", fx.Point3D(index * 150, 0))
            fx.activeSession().addNode(newroto)

            inputname = "input" + str(index + 2)
            output_node.addPort()

            newroto.port("foreground").connect(OG_ROTO_NODE.port("foreground").source)
            newroto.port("output").connect(output_node.port(inputname))

            layer.visible = False

    def PkgPaint(self, nodename):
        """Modify the active session for exporting a paint task through Deadline. This functions will alter the active session and add the proper node to render all paint strokes in the alpha of a new outputnode"""

        # CHECK IF PROJECT ALREADY CONTAINS A DEADLINE_RENDER Session
        for session in fx.activeProject().sessions:
            if session.label == "DEADLINE_RENDER":
                fx.activeProject().removeItem(session)

        ## GET PROPER PATH
        output_file = os.path.join(
            os.getenv("PXO_FRAMESTORE_ROOT"),
            os.getenv("PXO_PROJECT"),
            os.getenv("PXO_SEQUENCE"),
            os.getenv("PXO_SHOT"),
            "elements/2d/paint/silhouette_paint",
            getProjectName(),
        ).replace("\\", "/")

        # GET THE PAINT NODE
        PAINT_NODE = fx.activeSession().node(nodename)

        # ADD OUTPUT NODE
        RemoveBadOutputs()

        output_node = fx.Node("OutputNode", label="DEADLINE_RENDER_NODE")
        output_node.setState("graph.pos", fx.Point3D(0, 300))
        output_node.properties["path"].value = output_file
        output_node.properties["channels"].value = 3
        output_node.properties["views"].value = 1
        fx.activeSession().addNode(output_node)

        PAINT_NODE.port("output").connect(output_node.port("input"))


class DeadlineRender(fx.Action):
    """Creates the action for silhouette to be able to call it later."""

    def __init__(self):
        fx.Action.__init__(self, "PXO|Send to Deadline (F12)")

    def execute(self):
        window = GUI()
        window.exec()


def runDeadlineRender():
    """This is a single fucntion that will build the whole GUI and present the user with the full experience to render into deadline. Defining this command is essential for keybinding"""
    window = GUI()
    window.exec()


fx.addAction(DeadlineRender())
fx.bind("F12", runDeadlineRender)