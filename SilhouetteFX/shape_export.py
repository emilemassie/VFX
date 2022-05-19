"""Silhouette Action for exporting Shapes."""

# Import built-in modules
import os
import tempfile

# Import third-party modules
from Qt import QtWidgets
import fx


NUKE_IO_MODULE = "Nuke 9+ Shapes"


class RotoExporter(object):
    """Roto Exporter Action Class."""

    def __init__(self):
        """Constructor."""
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.tempfile = os.path.join(tempfile.gettempdir(), "tempshape.nk")
        self.data = ""  # noqa: WPS110
        self.NODE_LIST = []
        self.SHAPE_LIST = []
        self.succesIcon = """<!DOCTYPE html><head><meta charset="utf-8"></head><body style="font:6px Courier New;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,g@Ng&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;,gggw,&nbsp;&nbsp;,g@N,,g@@@@@@@@P&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@N@@@@@@&nbsp;@@@@@@N*`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@@@@@@*,@@N*`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]@@@@@@@@P;g@`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@P)g@@@@@&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*B@P"g@@@@@@@@@p&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]@@@@@@@@@@g&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@@@@@K&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@B@@@@@N&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@&nbsp;&nbsp;%@@@@@@&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@&nbsp;&nbsp;&nbsp;&nbsp;]@@@@@@&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;@@@@@@@&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]@@@@@@p&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]@@@@@@K&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"@@@@@@g&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"@@@@@@-&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;B@@@@@&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`*NNP"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]NNP&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br></body></html>
        """

    def statusUpdate(self, txt):
        """Prints and sets the status of Silhouette.

        Information is printed into the bottom bar so that the user can see where
        the script is at in both the console and the normal GUI.

        Args:
            txt (str): Text to be used for the status update.

        """
        fx.status(str(txt))
        print(str(txt))  # noqa: WPS421

    def GetShapes(self, node):
        """Get shapes method.

        Puts all the shapes of a given RotoNode into a organized list.
        The organized list contains multiple levels of Layer/SubLayers.
        It grabs the top Layers only and organizes the other shapes that are under each top layer.

        Args:
            node (fx.Node): Node to use to extract the shapes.

        """
        for it in node.children:
            self.SHAPE_LIST.append(it)
            if it.isType("Layer"):
                self.GetShapes(it)

    def TempRender(self, node):
        """Temp render method.

        This TempRender Methode calls GetShapes() for every Layer in the given RotoNode.
        The shapes are then converted to nuke rotoShapes in a temporary file that gets deleted after.

        Args:
            node (fx.Node): Node to use for the temp render.

        Returns:
            str: Node data.

        """
        node_data = ""
        self.SHAPE_LIST = []
        self.GetShapes(node)
        fx.select(self.SHAPE_LIST)
        if fx.io_modules[NUKE_IO_MODULE].can_export and self.SHAPE_LIST:
            fx.io_modules[NUKE_IO_MODULE].export(self.tempfile)

            with open(self.tempfile) as tf:
                node_data = tf.read()
                node_data = node_data.replace(
                    'name '+fx.activeProject().name,
                    'name '+node.label.replace(" ", "_")

#'{0}"\ninputs 0'.format(node.label.replace(" ", "_")),

                )
            
        return node_data

    def run(self):
        """Run method.

        The run methode gets called by the user.
        It will run the full scripts and set all the functions variables.
        It will check for user errors (such as not selecting the proper node).
        This should stop the script before running into error and make sure
        all variable are properly assigned.

        """
        if fx.selection() and fx.selection()[0].isType("RotoNode"):
            for it in fx.selection()[0].children:
                if it.isType("Layer"):
                    self.NODE_LIST.append(it)
            for node in self.NODE_LIST:
                self.statusUpdate("Exporting layer : {0}".format(node.label))
                self.data = "{0}\n{1}".format(  # noqa: WPS110
                    self.data, self.TempRender(node)
                )

            os.remove(self.tempfile)

            self.statusUpdate("\n\nCopying to the clipboard...")
            self.clipboard.setText(self.data)

            self.statusUpdate("\n\nSUCCESS !!!\n\n\n ")

            fx.displayInformation(
                '<center style="font: 12px">ADDED TO THE CLIPBOARD !!!\n\n\n</center>'
                + self.succesIcon,
                title="SUCCESS !!!",
            )
        else:
            fx.displayError(
                "<center>Cannot find Main Roto Node <br> Please make sure to select a Roto Node in the Tree view before running the script !",
                title="WHERE MY NODE AT ??? ",
            )


class ExportShapes(fx.Action):
    """Export all shapes of one roto node into multiple nuke roto nodes."""
    
    def __init__(self):
        """Defines the object as a SilhouetteFX Action."""
        super(ExportShapes, self).__init__(
            "PXO|Export top Layers to Nuke Nodes (Ctlr+Alt+C)"
        )

    def available(self):
        """Checks if the menu item should be able to be pressed."""
        if fx.selection() and fx.selection()[0].isType("RotoNode"):
            AssertionError(True)
        else:
            AssertionError(False)

    def execute(self):
        """Defines the part of the script that should be executed when the action gets triggered."""
        re = RotoExporter()
        re.run()


def runShapeExporter():
    """Method for Keybind."""
    re = RotoExporter()
    re.run()


fx.addAction(ExportShapes())
fx.bind("Ctrl+Alt+c", runShapeExporter)
