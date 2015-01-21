

from qtPrintFramework.pageSetup.printerable import Printerable
#from qtPrintFramework.pageSetup.pageSetup import PageSetup
from qtPrintFramework.pageSetup.pageLayout import PageLayout


class PrinteredPageSetup(Printerable, PageLayout):
  '''
  A PageSetup that communicates with a PrinterAdaptor (by inheriting mixin Printerable)
  
  !!! This does NOT drag in Qt's QPrintSupport module.
  It understands PrintAdaptor, but does not require any imports of same.
  '''
  pass  # All data/behaviour in superclasses
  