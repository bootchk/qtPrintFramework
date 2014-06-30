
import syslog


def alertLog(message):
  '''
  Important failure to syslog and console.
  
  OSX only logs above ALERT
  After OSX 10.8, stderr and stdout are to /dev/null ?
  
  message should be ascii, else print() to console may throw decoding exception
  '''
  try:
    syslog.syslog(syslog.LOG_ALERT, message)
    print(message)
  except:
    pass
  
  
  
def debugLog(message):
  # Uncomment return to debug
  return
  print(message)