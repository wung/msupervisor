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

# header 
# requires: stylesheet
header = """
<!DOCTYPE html>
<html>
<title>mSupervisor</title>
<link href="%s" rel="stylesheet" type="text/css" />
<body>
<div class="container">
<div class="header">mSupervisor</div>

""" 

# message section
# requires: style, style, message
message = """
<div class="line%s"><span class="msg_%s">%s:</span> %s</div>
"""

message_div = """
<div class="msg_box">
"""

message_end_div = """
</div>
"""

# footer 
# requires: version
footer = """
</div>
<div class="footer"><a href="http://github.com/bungow/msupervisor/">mSupervisor</a> %s</div>
</body>
</html>
"""

########################################################################
# process section ######################################################
########################################################################

# process supervisor name
# requires: name, name, system_version, server_actions
supervisor_name = """
<div class="server_name" name="%s">%s</div>
<div class="server_actions">%s %% %s</div>
<div class="process_container">
"""


# groupline
# requires: group, server_id, group_id
groupline = """
<table>
<tr class="groupline">
    <td colspan="3">group %s</td>
    <td class="groupactions">[<a href="/restart/?svi=%s&amp;gpi=%s">restart all</a>] [<a href="/stop/?svi=%s&amp;gpi=%s">stop all</a>]</td>
</tr>
"""

#nogroupline
nogroupline = """
<table>

"""


# process list
# requires: line_color, statename, statename, name,
#           description, action, stop_url, log_url, tail_url, clear_url
process_list = """
<tr class="line%s">
    <td class="state"><span class="%s">%s</span></td>
    <td class="name">%s</td>
    <td class="description">%s</td>
    <td class="action">[%s] [<a href="%s">stop</a>] [<a href="%s" target="_blank">log</a>] [<a href="%s" target="_blank">tail</a>] [<a href="%s">clearlog</a>]</td>
</tr>
""" 

process_finish = """
</table>
</div>
"""

########################################################################
# offline servers section
########################################################################

# offline server header
offline_header = """
<div class="offline_server_section">offline servers</div>
<div class="process_container">
"""

# offline server name
# requires: line, server_name, error
offline_server_name = """
<table>
<tr class="line%s">
    <td class="offline_server_name">%s</td>
    <td class="offline_server_problem">%s</td>
</tr>
</table>
"""



