
from qtEmbeddedQmlFramework.embeddedQmlManager import EmbeddedQmlManager
from qtEmbeddedQmlFramework.embeddedQmlInterface import EmbeddedQmlInterface

from qtPrintFramework.pageLayout.pageLayout import PageLayout

from qtPrintFramework.pageLayout.components.orientation import Orientation
from qtPrintFramework.pageLayout.components.paper.standard import StandardPaper


class PageSetupDialogQMLManager():
  '''
  Understands delegate to QML view (dialog) on a PageLayout model.
  The delegate is both the model and knows how to invoke the view.
  The QML instantiates the delegate/model.
  
  ??? Does an app need to switch between pageLayoutTypes (printered and unprinted) during an app session?
  I.E. if a user adds a printer subsystem to their device while the app is running,
  should the app recognize this and switch to a printered page layout?
  This is an issue mainly on mobile devices.
  On a desktop, users routinely restart apps anyway.
  On a mobile, users don't usually restart apps.
  But on mobile devices, users don't usually add printers: either the OS has a printing subsystem or not.
  '''
  
  def __init__(self, pageLayoutType):
    '''
    Create delegate to PageSetup dialog implemented in QML.
    
    pageLayoutType is PrinteredPageLayout or UnprinteredPageLayout
    '''
    self.delegates = {}
    
    self.manager = EmbeddedQmlManager(subsystemName='print')
    self._registerOtherTypes(qmlManager=self.manager)
    
    interfaces = [EmbeddedQmlInterface(pageLayoutType, 'pageSetup', 'DelegatedPageSetup.qml', 
                                         modelDelegateName='pageSetupDelegate',
                                         modelContextMenuName=None)
                    ]
    " Create QQuickView widgets from QML.  Put delegates in delegateMgr. "
    " Keep reference so quickviews not garbage collected. "
    self.manager.createInterfaces(self.delegates, interfaces)
    
    '''
    Assert delegate in self.delegates{} 
    implements API QmlDelegate having a activate() method for displaying dialog.
    
    The dialog's controls work directly on properties of a PageLayout instance.
    Acceptance/Cancellation of dialog is moot.
    No business logic communication to delegate other than to activate (show) it.
    '''
    
    
  def _registerOtherTypes(self, qmlManager):
    # register other types used by QML
    qmlManager.registerTypeInQml(typeToRegister=Orientation)
    qmlManager.registerTypeInQml(typeToRegister=StandardPaper)
    
    
  def pageSetupDialogDelegate(self):
    result = self.delegates['pageSetupDelegate']
    assert isinstance(result, PageLayout) # a superclass of PageLayout
    return result
