
import os
import socket
import subprocess
from tkinter import messagebox
import console_ctrl
import sys
from time import sleep
import time
import csv
from pathlib import Path, PosixPath

from normal import method

def initialization(path):

    try: 
        method.FileDelete(method.PathJoin(path, 'PASS'))
        method.FileDelete(method.PathJoin(path, 'FAIL'))
        method.FileDelete(method.PathJoin(path, 'STOP'))
        
        config = method.PyConfigParser()
        config.read(method.PathJoin(path, 'config.ini'))

        #[env]
        output_file_name = method.ConfigGet(config, 'env', 'output_file_name', 'output.txt')
        method.FileDelete(method.PathJoin(path, output_file_name))

        #[logger]
        logger_file_name = method.ConfigGet(config, 'logger', 'file_name', 'sys.log')
        method.FileDelete(method.PathJoin(path, logger_file_name))

        return config
    
    except Exception as e:
        method.Logging(config, path, 'ERROR', '{}'.format(e))
        raise


def subprocess_popen(command, flag, timeout, popen, fd_r, fd_w, interface):
    
    try:

        method.Logging(config, path_current_dir, 'INFO', 'popen "{}"'.format(interface))
        popen = subprocess.Popen([interface], stdin=subprocess.PIPE, stdout=fd_w, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)

    except Exception as e:
        raise RuntimeError(e)
    

    return popen

def subprocess_write(command, flag, timeout, popen, fd_r, fd_w, interface = None):
    
    try:

        if command :
            method.Logging(config, path_current_dir, 'INFO', '{}'.format(command))
            if command == '^C' :
                console_ctrl.send_ctrl_c(popen.pid)
            else:
                popen.stdin.write('{}\n'.format(command))

        
        data = subprocess_read(command, flag, timeout, popen, fd_r, fd_w, interface)
 

    except Exception as e:
        raise RuntimeError(e)
    

    return data

def subprocess_read(command, flag, timeout, popen, fd_r, fd_w, interface = None):
    
    try:

        timeout = float(timeout)
        time_start = time.perf_counter()
        data = ''
        while(True):

            sleep(0.5)
            data += fd_r.read()
            if flag and flag in data: break
            time_end = time.perf_counter()
            if timeout != -1 and (time_end - time_start) > timeout: break

        method.Logging(config, path_current_dir, 'INFO', '{}'.format(data))

    except Exception as e:
        raise RuntimeError(e)
    

    return data

def subprocess_run(popen, **kwargs):
    
    try: 

        result = False
        data = ''

        for i in range(1):

            command = kwargs.get('command', '')
            flag = kwargs.get('flag', '')
            timeout = kwargs.get('timeout', '5')
            loop = kwargs.get('loop', 'Flase')
            test_pass = kwargs.get('test_pass', '')
            test_fail = kwargs.get('test_fail', '')
            delay_time = kwargs.get('delay_time', '0')
            interface = kwargs.get('interface', '0')

            if '(path)' in command: command = command.replace('(path)', path_current_dir)
            if '(path)' in interface: interface = interface.replace('(path)', path_current_dir)

            if command == 'delay':
                if int(delay_time) != 0 :
                    method.Logging(config, path_current_dir, 'INFO', 'delay({})'.format(delay_time))
                    sleep(int(delay_time))

            else:

                if command == 'open':
                    command = ''
                    popen = subprocess_popen(command, flag, timeout, popen, fd_r, fd_w, interface)

                if popen == None:
                    raise RuntimeError('subprocess no open')
                    break

                data = subprocess_write(command, flag, timeout,  popen, fd_r, fd_w)

                if test_pass : 
                    if test_pass not in data :
                        result = False
                        break
                if test_fail:
                    if test_fail in data :
                        result = False
                        break

                if loop == 'True':
                    while(True):
                        if method.PathIsExist(method.PathJoin(path_current_dir, 'STOP')) == True: 
                            break
                        sleep(1)

            result = True

    except Exception as e:
        raise e
    finally:
        if result == True and not data: data = 'done.'
        elif result == False and not data: data = 'failed.'
        return popen, result, data
    
if __name__ == '__main__':
    pass

    try:       
 
        path_current_dir = method.PathGetCurrent()
        config =  initialization(path_current_dir)
        
        mode = method.ConfigGet(config, 'env', 'mode', 'script')
        popen = None
        result = True
        data = ''
        method.FileDelete(method.PathJoin(path_current_dir, './sub.log'))
        fd_w = open(method.PathJoin(path_current_dir, './sub.log'), 'w')
        fd_r = open(method.PathJoin(path_current_dir, './sub.log'), 'r')
        
        if mode == 'script':
            with open(method.PathJoin(path_current_dir, 'script.txt'), newline='', encoding='utf-8') as csvfile:
                rows = csv.reader(csvfile)
                for row in rows:
                    data = ', '.join(row)
                    if not data or data[0] == '#': continue
                    kwargs = eval(data)
                    
                    popen, result, data = subprocess_run(popen, **kwargs)
                    if  result == False:
                        break
        elif mode == 'socket':
              
            HOST = '127.0.0.1'
            PORT = 8383
            conn = None
            end = False
            data = ''

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen(1)

            method.Logging(config, path_current_dir, 'INFO', 'socket server start at {}:{}'.format(HOST, PORT))

            while True:
                conn, addr = s.accept()
                method.Logging(config, path_current_dir, 'INFO', 'socket Connected by {}'.format(addr))
                conn.send('R: socket Connected by {}\r\n'.format(addr).encode())

                while True:
                    
                    try: 
                        recv = conn.recv(1024)
                        recv = recv.decode()
                        recv = recv.strip()
                        recv = recv.replace('\n', '').replace('\r', '') 
                        if not recv or recv == 'close':
                            data = 'close'
                            break
                        elif recv == 'exit':
                            data = 'exit'
                            break

                        kwargs = eval(recv)
                        if type(kwargs).__name__ != 'dict' :
                            data = 'Unknow'
                            continue

                        popen, result, data = subprocess_run(popen, **kwargs)
                    except Exception as e:
                        data = '{}'.format(e)
                        pass
                    finally:
                        if data: conn.send('R: {}\r\n'.format(data).encode())

                if data == 'exit': break
                elif data == 'close': conn.close()

    except Exception as e:
        result = False
        method.Logging(config, path_current_dir, 'ERROR', '{}'.format(e))
    
    finally:
        if mode == 'script':
            if popen != None:
                fd_w.close()
                fd_r.close()
                popen.kill()
            if result == True:
                method.FileCreate('{}\\PASS'.format(path_current_dir))
            else:
                method.FileCreate('{}\\FAIL'.format(path_current_dir))
        elif mode == 'socket':
            if conn != None:
                conn.close()

        
        method.Logging(config, path_current_dir, 'INFO', 'Finish.')
    
        
        