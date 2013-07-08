#!/usr/bin/python

import socket
import subprocess
import time
import os
from tempfile import *
import sys

HOST = socket.gethostbyname(socket.getfqdn())
PORT = 6668


def send_osa(script_path):
    cmd = ['osascript -e',
           '\'tell app "ZBrush"',
           'to open',
           '"' + script_path + '"\'']

    cmd = ' '.join(cmd)
    print cmd
    os.system(cmd)
    # time.sleep(1)
    # os.system(cmd.replace('.txt','.zsc'))


def zbrush_open(name):
    zs_temp = NamedTemporaryFile(delete=False, suffix='.txt')
    env = os.getenv('ZDOCS', "/your/file/path/for/zbrush/to/open/files")
    print env

    zscript = """
            [RoutineDef, open_file,
            [FileNameSetNext,"!:#FILENAME"]
            [VarSet,in_tool,#TOOLNAME]
            [VarSet,imp,0]
            [Loop, [SubToolGetCount],
            [VarSet, a, a+1]
            [SubToolSelect,a-1]
            [VarSet, sub, [FileNameExtract,[GetActiveToolPath],2]]
            [If, [StrFind, in_tool, sub]>-1,
                [IPress,Tool:Import]
                [VarSet,imp,1],]
            ]
            [If, imp<1,
                    [If, a==[SubToolGetCount],


                        [IPress,Tool:SubTool:Duplicate]
                        [IPress,Tool:SubTool:MoveDown]
                        [IPress,Tool:Geometry:Del Higher]
                        [IPress,Tool:Import]
                        [ToolSetPath,[SubToolGetCount],"!:#FILENAME"]
                        , [MessageOk, False]
                    ]
            ]
            ]
            [RoutineCall,open_file]
                """

    zscript = zscript.replace('#FILENAME',os.path.join(env, name))
    zscript = zscript.replace('#TOOLNAME',name.replace('.ma',''))
    #print zscript
    zs_temp.write(zscript)
    return zs_temp.name


def listen():

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(2)
    soc.bind((HOST, PORT))
    soc.listen(1)
    conn, addr = soc.accept()

    while 1:
        try:
            data = conn.recv(1024)
        except:
            print "err"
            break
        if not data:
            break
        if(data.split('|')[0] == 'open'):
            objs = data.split('|')[1].split(':')
            for obj in objs:
                print obj
                zs_temp = zbrush_open(obj+'.ma')
                send_osa(zs_temp)

    conn.close()
    print "end"

while 1:
    listen()