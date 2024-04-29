'''
Created on 2024年2月28日

@author: ericluo
'''
import os
from configparser import ConfigParser #ini file
import shutil
import logging.config
import ruamel.yaml

class PyConfigParser(ConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr
        
def DirectoryIsExist(path):
    return os.path.isdir(path)

def DirectoryDelete(path):
    try:
        shutil.rmtree(path)
    except :
        raise RuntimeError("DirectoryDelete Fail.\n{}".format(path))

def DirectoryMake(path):
    if DirectoryIsExist(path) == True: return
    
    path_split = os.path.split(path)
    if DirectoryIsExist(path_split[0]) == True: return
    
    path_drive = os.path.splitdrive(path_split[0])
    string_split = path_drive[1].split('\\')
    path_new = path_drive[0]
    
    for s in string_split :
        
        s.strip()      
        if not s: continue    
        path_new = "".join((path_new, '\\', s))  
        if DirectoryIsExist(path_new) ==  False: os.mkdir(path_new)
        
def FileisExist(path):
    return os.path.isfile(path)

def FileCopy(src, dst):
    if FileisExist(src):
        DirectoryMake(dst)
        shutil.copyfile(src, dst)
    
def FileExtension(path):  
    root, extension = os.path.splitext(path)  # @UnusedVariable
    return  extension

def FileList(path):  
    return os.listdir(path)
    
def FileCreate(path): 
    open(path, mode='w', encoding='utf-8')
    
def FileDelete(path): 
    if FileisExist(path) == True : os.remove(path)

def PathIsExist(path):  
    return os.path.exists(path)

def PathGetCurrent(new = ''):
    path = os.path.abspath(os.getcwd())
    return path

def PathJoin(path, *paths):      
    return os.path.join(path, *paths)

def ConfigRead(config, path):
    try:
        config.read(path)
        return True
    except Exception as e:
        print(e)
        return False

def ConfigGet(config, section, option, default):
    try:
        value = config.get(section, option, fallback=default)
    except Exception as e:
        print(e)
    finally:
        return value
    
def ConfigAdd(config, section, option, value):
    try:
        if not config.has_section(section) : config.add_section(section)     
        config.set(section, option, value)           
    except Exception as e:
        print(e)
    finally:
        return

def ConfigRemoveOption(config, section, option):
    try:
        if config.has_section(section) :  config.remove_option(section, option)         
    except Exception as e:
        print(e)
    finally:
        return

def ConfigRemoveSections(config, section):
    try:
        if config.has_section(section) :  config.remove_section(section)         
    except Exception as e:
        print(e)
    finally:
        return
     
def ConfigWrite(config, path):
    try:
        with open(path, 'w') as conf:
            config.write(conf)
    except Exception as e:
        print(e)
    finally:
        return
    
def YamlLoad(path, encode="utf-8"):       
    try:
        if PathIsExist(path) == False: 
            raise RuntimeError("Yaml file Not Exist.\n{}".format(path))                       
        with open(path, 'r', encoding=encode) as stream:
            return ruamel.yaml.load(stream, Loader=ruamel.yaml.RoundTripLoader)      
    except:       
        raise RuntimeError("YamlLoad Fail.\n{}".format(path))
             
  
def YamlDump(path, config, encode="utf-8"):     
    try:                             
        with open(path, 'w', encoding=encode) as stream:
            ruamel.yaml.dump(config, stream, Dumper=ruamel.yaml.RoundTripDumper)                  
    except:       
        raise RuntimeError("YamlDump Fail.\n{}".format(path))
   
def Indent(message):

    data = ""
    for s in message.split("\n"):
        
        s.strip()
        if not s:
            data = "".join((data, "\n"))
        elif not data:
            data = "".join((s))
        else:
            data = "".join((data, "\n{:<31}".format(" "), s))

    data.strip()
    
    return data 
 
def LoggerLoad(loggers, filename, level):

    try:

        logger = None

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'normal': {  # the name of formatter
                    'format': '[%(asctime)s %(levelname)8s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {  # the name of formatter
                    'format': '[%(asctime)s %(levelname)8s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'console': {  # the name of handler
                    'class': 'logging.StreamHandler',  # emit to sys.stderr(default)
                    'level': '{}'.format(level),
                    'formatter': 'normal',  # use the above "normal" formatter
                    'stream': 'ext://sys.stdout',
                },
                'file': {  # the name of handler
                    'class': 'logging.FileHandler',  # emit to disk file
                    'level': '{}'.format(level),
                    'filename': '{}'.format(filename),  # the path of the log file
                    'formatter': 'normal',  # use the above "normal" formatter
                    # 'maxBytes': '5242880',
                    # 'backupCount': '1',
                    # 'encoding': 'utf8',
                },
                # 'time-rotating-file': {  # the name of handler
                    # 'class': 'logging.handlers.TimedRotatingFileHandler',  # the log rotation by time interval
                    # 'filename': 'time_rotating.log',  # the path of the log file
                    # 'when': 'midnight',  # time interval
                    # 'formatter': 'normal',  # use the above "simple" formatter
                # },
            },
            'loggers': {
                'console': {  # the name of logger
                    'handlers': ['console'],  # use the above "console1" and "console2" handler
                    'level': 'INFO',  # logging level
                },
                'file': {  # the name of logger
                    'handlers': ['file'],  # use the above "file1" handler
                    'level': 'INFO',  # logging level
                    'propagate': True,
                },
                # 'time-file': {  # the name of logger
                    # 'handlers': ['time-rotating-file'],  # use the above "time-rotating-file" handler
                    # 'level': 'INFO',  # logging level
                    # 'propagate': True,
                # },
                'all': {  # the name of logger
                    'handlers': ['console', 'file'],  # use the above "console1" and "console2" handler
                    'level': 'INFO',  # logging level
                    'propagate': True,
                },
            },
            'module': {
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }

        logging.config.dictConfig(config=LOGGING)
        logger = logging.getLogger(loggers)

    except Exception as e:    
        print(e)
    finally:
        if logger.hasHandlers() == False:
            return None
        else:
            return logger

def Logging(config, path, level, message):
    
    try:

        logger = None
            
        #[logger]
        loggers = ConfigGet(config, 'logger', 'loggers', 'all')
        file_name = ConfigGet(config, 'logger', 'file_name', 'system.log')
        level = ConfigGet(config, 'logger', 'level', 'INFO')
        
        # logger = LoggerLoad(loggers, logger_file_name, logger_level)
        # if logger == None: raise RuntimeError("LoggerLoad Fail.")
        
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'normal': {  # the name of formatter
                    'format': '[%(asctime)s %(levelname)8s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'simple': {  # the name of formatter
                    'format': '[%(asctime)s %(levelname)8s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
            },
            'handlers': {
                'console': {  # the name of handler
                    'class': 'logging.StreamHandler',  # emit to sys.stderr(default)
                    'level': '{}'.format(level),
                    'formatter': 'normal',  # use the above "normal" formatter
                    'stream': 'ext://sys.stdout',
                },
                'file': {  # the name of handler
                    'class': 'logging.FileHandler',  # emit to disk file
                    'level': '{}'.format(level),
                    'filename': '{}'.format(PathJoin(path, file_name)),  # the path of the log file
                    'formatter': 'normal',  # use the above "normal" formatter
                    # 'maxBytes': '5242880',
                    # 'backupCount': '1',
                    # 'encoding': 'utf8',
                },
                # 'time-rotating-file': {  # the name of handler
                    # 'class': 'logging.handlers.TimedRotatingFileHandler',  # the log rotation by time interval
                    # 'filename': 'time_rotating.log',  # the path of the log file
                    # 'when': 'midnight',  # time interval
                    # 'formatter': 'normal',  # use the above "simple" formatter
                # },
            },
            'loggers': {
                'console': {  # the name of logger
                    'handlers': ['console'],  # use the above "console1" and "console2" handler
                    'level': 'INFO',  # logging level
                },
                'file': {  # the name of logger
                    'handlers': ['file'],  # use the above "file1" handler
                    'level': 'INFO',  # logging level
                    'propagate': True,
                },
                # 'time-file': {  # the name of logger
                    # 'handlers': ['time-rotating-file'],  # use the above "time-rotating-file" handler
                    # 'level': 'INFO',  # logging level
                    # 'propagate': True,
                # },
                'all': {  # the name of logger
                    'handlers': ['console', 'file'],  # use the above "console1" and "console2" handler
                    'level': 'INFO',  # logging level
                    'propagate': True,
                },
            },
            'module': {
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }

        logging.config.dictConfig(config=LOGGING)
        logger = logging.getLogger(loggers)

    except Exception as e:    
        print(e)
    finally:
        if logger != None and logger.hasHandlers() == True:
            if level == "INFO":
                logger.info("{}".format(Indent(message)))
            elif level == "DEBUG":
                logger.debug("{}".format(Indent(message)))
            elif level == "WARNING":
                logger.warning("{}".format(Indent(message)))
            elif level == "ERROR":
                logger.error("{}".format(Indent(message)))
            elif level == "CRITICAL":
                logger.critical("{}".format(Indent(message)))
                
        del logger
# def Logging(logger, level, message):
#
#     if logger == None:
#         print(message)
#     else:
#         if level == "INFO":
#             logger.info("{}".format(Indent(message)))
#         elif level == "DEBUG":
#             logger.debug("{}".format(Indent(message)))
#         elif level == "WARNING":
#             logger.warning("{}".format(Indent(message)))
#         elif level == "ERROR":
#             logger.error("{}".format(Indent(message)))
#         elif level == "CRITICAL":
#             logger.critical("{}".format(Indent(message)))