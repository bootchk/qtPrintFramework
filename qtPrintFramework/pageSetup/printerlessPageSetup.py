

from qtPrintFramework.pageSetup.pageSetup import PageSetup


class PrinterlessPageSetup(PageSetup):
  '''
  A PageSetup that does NOT communicate with a PrinterAdaptor
  '''
  pass  # All data/behaviour in subclasses
  