#!/usr/bin/env python

########################################################################
# The MIT License (MIT)
#
# Copyright (c) 2014 <bungow@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
########################################################################

import xmlrpclib, ConfigParser, sys, socket
from wsgiref.simple_server import make_server
from wsgiref.util import shift_path_info
from cgi import parse_qs, escape
from datetime import datetime, timedelta
import htemplate

_version = 0.1

# Variable initalization
config = ConfigParser.ConfigParser()
servers = []
config_file = "msupervisor.ini"
messages = []
server_num = 0

# Load config file
try:
    config.read(config_file)
    servers = config.items("servers")
    css_file = config.get('config','stylesheet')
    
except:
    messages.append(("error", "Error loading config file: %s"%(config_file)))

# Connect to servers

server_list = []
servers_offline = []

for i in servers:
    
    try:
        x = xmlrpclib.Server(i[1])
        x.supervisor.getState()
        server_list.append((server_num, i[0], x))
        server_num = server_num + 1
    except xmlrpclib.ProtocolError, e:
        servers_offline.append((i[0], "Unauthorized %s" %(e)))
    except socket.gaierror, e:
        servers_offline.append((i[0], "%s" %(e)))
    except socket.error, e:
        servers_offline.append((i[0], "%s" %(e)))
    except e:
        servers_offline.append((i[0], "Unexpected error: %s" %(e)))


def secondsToDHMS(seconds):
    days = str(seconds // (3600 * 24))
    hours = str((seconds // 3600) % 24)
    minutes = str((seconds // 60) % 60)
    seconds = str(seconds % 60)
    if len(hours) <= 1:
        hours = "0" + hours
    if len(minutes) <= 1:
        minutes = "0" + minutes
    if len(seconds) <= 1:
        seconds = "0" + seconds

    return days, hours, minutes, seconds


def calcTime(now, start, stop, running):
    if not running:
        return "stop: " + datetime.fromtimestamp(stop).strftime('%d-%m-%Y %H:%M:%S')
    else:
        seconds = now - start
        day, hour, minute, second = secondsToDHMS(seconds)
        if day == 0:
            return "up time: %s:%s:%s" %(hour, minute, second)
        elif day == 1:
            return "up time: %s day %s:%s:%s" %(day, hour, minute, second)
        else:
            return "up time: %s days %s:%s:%s" %(day, hour, minute, second)


def serverOfflineList(server):
    line = 0
    offline_html = ""
    for i in server:
        
        if(line):
            line = 0
        else:
            line = 1
        offserver = htemplate.offline_server_name %(line,i[0],i[1])
        offline_html = offline_html + offserver 
        
    return htemplate.offline_header + offline_html + htemplate.message_end_div


def serverOnlineList(server):
    online_html = " "
    for i in server:
        line = 0
        process_list = " "
        system_version = i[2].supervisor.getSupervisorVersion()
        process = i[2].supervisor.getAllProcessInfo()
        sactions = "[<a href=\"/restart/?svi=%s\">restart all</a>] | [<a href=\"/stop/?svi=%s\">stop all</a>]" %(i[0], i[0])
        
        header = htemplate.supervisor_name % (i[1], i[1], system_version, sactions)
                 
        counter = {}
        for z in process:
            if z["group"] not in counter:
                counter[z["group"]] = 1
            else:
                counter[z["group"]] = counter[z["group"]] + 1
            
        lastgroup = ""
        for x in process:

            if (x["group"] != lastgroup):
                if lastgroup:
                    process_list = process_list + "</table>"
                
                if (counter[x["group"]] > 1):
                    process_list = process_list + htemplate.groupline %(x["group"], i[0], x["group"],i[0], x["group"])
                else:
                    process_list = process_list + htemplate.nogroupline
                 
            lastgroup = x["group"]
            
            
            
            if(line):
                line = 0
            else:
                line = 1
            

            # put urls
            if x["statename"] == "RUNNING":
                running = 1
                action = "<a href=\"/restart/?svi=%s&amp;gpi=%s&amp;pci=%s\">restart</a>" %(i[0], x["group"], x["name"])
            else:
                running = 0
                action = "<a href=\"/start/?svi=%s&amp;gpi=%s&amp;pci=%s\">start</a>" %(i[0], x["group"], x["name"])
                
            stop_url = "/stop/?svi=%s&amp;gpi=%s&amp;pci=%s" %(i[0], x["group"], x["name"])
            log_url = "/log/?svi=%s&amp;gpi=%s&amp;pci=%s" %(i[0], x["group"], x["name"])
            tail_url = "/tail/?svi=%s&amp;gpi=%s&amp;pci=%s" %(i[0], x["group"], x["name"])
            clear_url = "/clear/?svi=%s&amp;gpi=%s&amp;pci=%s" %(i[0], x["group"], x["name"])

            # calcule time
            time = calcTime(x["now"], x["start"], x["stop"], running)
            
            # generate description
            description = ""
            if running:
                description = description + "pid: %s | %s" %(x["pid"], time)
            else:
                description = description + "%s <br> %s" %(time, x["spawnerr"])
    
            process_list = process_list + \
                        htemplate.process_list % (line, x["statename"],
                        x["statename"].lower(), x["name"], description, action,
                        stop_url, log_url, tail_url, clear_url)

        online_html = online_html + header + process_list + htemplate.process_finish

    return online_html


def messagesPrint():
    global messages
    line = 0;
    messages_html = htemplate.message_div
    
    if not messages:
        return ""
    
    for i in messages:
        if(line):
            line = 0
        else:
            line = 1
        messages_html = messages_html + htemplate.message %(line, i[0], i[0],  i[1])
    messages_html = messages_html + htemplate.message_end_div
    messages=[]
    return messages_html


def startProcess(server_id, group_id, process_id):
    if process_id:
        try:
            server_list[int(server_id)][2].supervisor.startProcess((group_id + ":" + process_id))
            messages.append(("success","%s:%s started" %(group_id, process_id)))
        except xmlrpclib.Fault:
            messages.append(("error","%s:%s not started" %(group_id, process_id)))
        return
        
    elif group_id:
        try:
            server_list[int(server_id)][2].supervisor.startProcessGroup(group_id)
            messages.append(("success","All group %s process started" %(group_id)))
        except:
            messages.append(("error","Can't start group %s process" %(group_id)))
            
    elif server_id:
        try:
            server_list[int(server_id)][2].supervisor.startAllProcesses()
            messages.append(("success","All process started in %s" %(server_list[int(server_id)][1])))
        except:
            messages.append(("error","Can't start all process in %s" %(server_list[int(server_id)][1])))
        return


def stopProcess(server_id, group_id, process_id):
    if process_id:
        try:
            server_list[int(server_id)][2].supervisor.stopProcess((group_id + ":" + process_id))
            messages.append(("success","%s:%s stopped" %(group_id, process_id)))
        except xmlrpclib.Fault:
            messages.append(("info","%s:%s is not running" %(group_id, process_id)))
        
    elif group_id:
        try:
            server_list[int(server_id)][2].supervisor.stopProcessGroup(group_id)
            messages.append(("success","All group %s process stopped" %(group_id)))
        except:
            messages.append(("error","Can't stop group %s process" %(group_id)))
        
    elif server_id:
        try:
            server_list[int(server_id)][2].supervisor.stopAllProcesses()
            messages.append(("success","All process stopped in %s" %(server_list[int(server_id)][1])))
        except:
            messages.append(("error","Can't stop all process in %s" %(server_list[int(server_id)][1])))
        return
        

def readProcessLog(server_id, group_id, process_id, mode=0):
    if (mode == 0):
        raw = server_list[int(server_id)][2].supervisor.readProcessStdoutLog((group_id + ":" + process_id), -1024, 0)
        log = "<br />".join(raw.split("\n"))
        return log

def clearProcessLog(server_id, group_id, process_id):
    try:
        server_list[int(server_id)][2].supervisor.clearProcessLog((group_id + ":" + process_id))
        messages.append(("success","%s:%s log cleared" %(group_id, process_id)))
    except xmlrpclib.Fault:
        messages.append(("error","%s:%s can't clear log" %(group_id, process_id)))


def application(environ, start_response):
    
    status = '303 See Other'
    response_headers = [('Location','/')]
    response_body = " "
    html_data = " "
    filepath = shift_path_info(environ)

    # Get args values
    args = parse_qs(environ['QUERY_STRING'])
    server_id = escape(args.get('svi' , [''])[0])
    group_id = escape(args.get('gpi' , [''])[0])
    process_id = escape(args.get('pci' , [''])[0])


    if not filepath:
        html_data = html_data + serverOnlineList(server_list)

        if(servers_offline):
            html_data = html_data + serverOfflineList(servers_offline)

        response_body = htemplate.header %(css_file) + messagesPrint() + html_data + htemplate.footer %(_version)
        
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]

    elif (filepath == css_file):
        try:
            cssf = open(css_file, 'r')
            css = cssf.read()
            cssf.close()
            response_body = css
        except:
            response_body = ".msg_error { color: #cc0000; }"
            messages.append(("error", "Error loading stylesheet file: %s"%(css_file)))
            
        status = '200 OK'
        response_headers = [('Content-Type', 'text/css'),
                            ('Content-Length', str(len(response_body)))]


    elif (filepath == "start"):
        startProcess(server_id, group_id, process_id)


    elif (filepath == "restart"):
        stopProcess(server_id, group_id, process_id)
        startProcess(server_id, group_id, process_id)


    elif (filepath == "stop"):
        stopProcess(server_id, group_id, process_id)


    elif (filepath == "log"):
        response_body = "<pre>" + readProcessLog(server_id, group_id, process_id) + "</pre><p><a href=\"\">Test link</a></p>"
        
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]


    elif (filepath == "clear"):
        clearProcessLog(server_id, group_id, process_id)

    else:
        status = '403 Forbidden'
        response_body = "<h1>403 Forbidden</h1>"
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(response_body)))]
        
                        
    start_response(status, response_headers)
    return [response_body]


# Start server
httpd = make_server('localhost', 8051, application)
httpd.serve_forever()
