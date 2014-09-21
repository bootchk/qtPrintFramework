

from qtPrintFramework.pageSetup.printerable import Printerable
from qtPrintFramework.pageSetup.pageSetup import PageSetup


class PrinteredPageSetup(Printerable, PageSetup):
  '''
  A PageSetup that communicates with a PrinterAdaptor
  
  !!! This does NOT drag in Qt's QPrintSupport module.
  It understands PrintAdaptor, but does not require any imports of same.
  '''
  pass  # All data/behaviour in subclasses
  