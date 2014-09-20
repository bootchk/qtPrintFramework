'''
Exceptions do not depend on existence of print subsystem, i.e. library QtPrintSupport.
'''

'''
User chose paper and margins yielding invalid pageSize.
'''
class InvalidPageSize(Exception):
  pass