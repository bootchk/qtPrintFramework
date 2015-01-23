
CRUFT?

from PyQt5.QtCore import QObject  # , QUrl
from PyQt5.QtCore import pyqtSignal as Signal


class PageSetupDialogDelegate(QObject):
  '''
  QML GUI form of PageSetupDialog
  '''

  accepted = Signal()
  rejected = Signal()

  def __init__(self, parentWindow, formation, titleParts):  # , flags=Qt.Dialog, ):
    
    # TODO, parentWindow should be the document, which may not be the activeWindow?
    # parentWindow = QCoreApplication.instance().activeWindow()
    super(PageSetupDialogQML, self).__init__() # parent=parentWindow, flags=flags)
    self.createDialog(parentWindow, prefix=titleParts[0].lower(), formation=formation)
    
    
  def createDialog(self, parentWindow, prefix, formation):
    '''
    Create QML based dialog.
    '''
    '''
    assert prefix in ['user', 'doc', 'line', ..., 'lineTool', ...]
    I.E. prefix identifies a member of a kind of style sheet: where kinds are [full, documenElement, tool]
    '''
    qmlFilename= styleResourceManager.styleQmlPath() + "styleSheets/"+prefix+"stylesheet.qml"  # e.g. Userstylesheet.qml
    
    qmlMaster = QmlMaster()
    qwin = qmlMaster.appQWindow()
    
    '''
    Order is important: create quickView, setContext, setSource, findComponent
    setContext defines names referred to in the source
    findComponent looks for names defined by the source.
    
    Note each .qml file has a DialogDelegate, all with same objectName "dialogDelegate" but separate instances.
    '''
    self.styleQuickView = qmlMaster.createQuickView(transientParent=qwin)
    self.exposeFormationModelToQML(view=self.styleQuickView, editedFormation=formation, prefix=prefix)
    # OLD self.styleQuickView = qmlMaster.quickViewForQML(qmlFilename, transientParent=qwin)
    qmlMaster.setSourceOnQuickView(view=self.styleQuickView, qmlFilename=qmlFilename)
    self.dialogDelegate = qmlMaster.findComponent(quickview=self.styleQuickView, 
                                                  className=QmlDelegate, 
                                                  objectName="dialogDelegate")
    assert self.dialogDelegate is not None
    
    "Wrap it, so it is visible?"
    " container takes ownership.  container is a widget"
    self.container = qmlMaster.wrapWidgetAroundQuickView(self.styleQuickView, parentWindow)
    
    " Remember view so later can update setContext? Not used?"
    config.QMLView = self.styleQuickView
  
  
  def open(self):
    '''
    execute the dialog.
    Just show() ing is not enough.
    Tell delegate to call QML Dialog method open()
    '''
    self.dialogDelegate.activate()
    
    
  def converseAppModal(self):
    '''
    Show:
    - Synchronous for some implementations (QWidget) (call doesn't return)
    - app modal (no other app windows take user input)
    - position in center in parent
    '''
    "TODO app modal"
    self.dialogDelegate.activate()
    
    
  def connectSignals(self, acceptSlot, cancelSlot):
    '''
    Self has-a dialogDelegate in QML.
    Connect its signals to given slots.
    '''
    self.dialogDelegate.accepted.connect(acceptSlot)
    self.dialogDelegate.rejected.connect(cancelSlot)
    