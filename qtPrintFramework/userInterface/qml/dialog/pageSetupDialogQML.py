
from qtEmbeddedQmlFramework.embeddedQmlManager import EmbeddedQmlManager
from qtEmbeddedQmlFramework.embeddedQmlInterface import EmbeddedQmlInterface

from qtPrintFramework.pageSetup.pageLayout import PageLayout

class PageSetupDialogQMLManager():
  
  def __init__(self):
    '''
    Create delegate to PageSetup dialog implemented in QML.
    '''
    self.delegates = {}
    
    interfaces = [EmbeddedQmlInterface(PageLayout, 'pageSetup', 'DelegatedPageSetup.qml', 
                                         modelDelegateName='pageSetupDelegate',
                                         modelContextMenuName=None)
                    ]
    " Create QQuickView widgets from QML.  Put delegates in delegateMgr. "
    " Keep reference so quickviews not garbage collected. "
    self.manager = EmbeddedQmlManager(self.delegates, interfaces)
    
    '''
    Assert delegate in self.delegates{} is instance of QmlDelegate having a activate() method for displaying dialog.
    
    The dialog's controls work directly on properties of a PageSetup instance.
    Acceptance/Cancellation of dialog is moot.
    No business logic communication to delegate other than to activate (show) it.
    '''
    
  def pageSetupDialogDelegate(self):
    result = self.delegates['pageSetupDelegate']
    assert isinstance(result, PageLayout)
    return result


pageSetupDialogMgr = PageSetupDialogQMLManager()