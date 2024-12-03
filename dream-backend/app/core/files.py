from app.core import util
import socket
import inspect, os, sys

## 신한카드 files 관리 모듈

class files : 
    def __init__(self, filename, filedate):
        if filedate == None or filedate == "" :
            filedate = util.getNow('%Y-%m-%d')

        self.send_path = f"/usr/src/app/data/offcard/files_send/{filename}/{filedate}/"
        self.recv_path = f"/usr/src/app/data/offcard/files_recv/{filename}/{filedate}/"
        util.makedirs(self.send_path)
        util.makedirs(self.recv_path)

    def DeleteAllFiles(self, filePath):
        if os.path.exists(filePath):
            for file in os.scandir(filePath):
                os.remove(file.path)
            return 'Remove All File'
        else:
            return 'Directory Not Found'

    def file_wirte(self, 블록, file_cont, mode):
        f = open(f"{self.send_path}block_{str(블록)}.txt", mode, encoding='utf-8')
        f.write(file_cont+"\n")
        f.close()
        return
    
    def block_list(self) :
        return os.listdir(self.send_path)
    
    def recv_list(self) :
        return os.listdir(self.recv_path)

    def recv_file_wirte(self, 블록, file_cont) :
        f = open(f"{self.recv_path}block_{str(블록)}.txt", "a", encoding='utf-8')
        f.write(file_cont+"\n")
        f.close()
        return
    
    def log_write(self, mode, msg) :

        print(f"{mode} [{util.getNow()}] {msg}")
        
        if mode == "recv" :
            file_path = self.recv_path
        elif mode == "send" :
            file_path = self.send_path
        else :
            return

        f = open(f"{file_path}{util.MMDDhhmmss()}_{str(id(self))}.log", "a", encoding='utf-8')
        f.write(f"[{util.getNow()}] "+msg+"\n")
        f.close()
        return


    
        