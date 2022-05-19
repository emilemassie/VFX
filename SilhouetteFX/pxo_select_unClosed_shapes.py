import fx

class SelectUnClosed(object):

	def __init__(self):

		self.unClosedList = []
		self.SHAPE_LIST = []

		if self.CheckNode():
			self.node = fx.selection()[0]
			self.GetShapes(self.node)
			self.SetSelection()
			fx.select(self.unClosedList)
			fx.displayError(r'<center>Selected a total of '+ str(len(self.unClosedList)) + ' unClosed shaped.<br>These shapes have been selected for you', title="UnClosed Shapes Selected ")
		else:
			fx.displayError("<center>Cannot find Main Roto Node <br> Please make sure to select a Roto Node in the Tree view before running the script !", title="WHERE MY NODE AT ??? ")

	def CheckNode(self):
		if fx.selection() and fx.selection()[0].isType("RotoNode"):
			return True
		else:
			return False

	def GetShapes(self, node):
		for it in node.children:
			self.SHAPE_LIST.append(it)
			if it.isType("Layer"):
				self.GetShapes(it)

	def SetSelection(self):
		for shape in self.SHAPE_LIST:
			if shape.isType("Shape"):
				if not shape.closed:
					self.unClosedList.append(shape)


class Select_unClosed(fx.Action):
    """Export all shapes of one roto node into multiple nuke roto nodes."""
    
    def __init__(self):
        """Defines the object as a SilhouetteFX Action."""
        super(Select_unClosed, self).__init__(
            "PXO|Select non-closed shapes"
        )

    def available(self):
        """Checks if the menu item should be able to be pressed."""
        if fx.selection() and fx.selection()[0].isType("RotoNode"):
            AssertionError(True)
        else:
            AssertionError(False)

    def execute(self):
        """Defines the part of the script that should be executed when the action gets triggered."""
        SelectUnClosed()
        

fx.addAction(Select_unClosed())

