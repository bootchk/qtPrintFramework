

from qtPrintFramework.pageLayout.able.printerable import Printerable
from qtPrintFramework.pageLayout.pageLayout import PageLayout


class PrinteredPageLayout(PageLayout, Printerable):
  '''
  A PageLayout that communicates with a PrinterAdaptor (by inheriting mixin Printerable)
  
  !!! This does NOT drag in Qt's QPrintSupport module.
  It understands PrintAdaptor, but does not require any imports of same.
  '''
  pass  # All data/behaviour in superclasses
  