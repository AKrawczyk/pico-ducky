# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Modified: Aaron Krawczyk ()
# Assistance: Cursor and Claud AI
# April 2025
# Fixes issue with webserver not writing new file
# or writing file after editing.
# Wirtes to file but overloads webserver on Pico W 2022.
# PICO 1, 2 and W board support

import socketpool
import os
import storage
import socketpool
import wifi
from adafruit_httpserver import Server, Request, JSONResponse ,POST , Response
from duckyinpython import *
import asyncio

# Create the web server with a pool that will be passed in
web_app = None

# Modification AK
# ASCII values for '{' and '}'
lcb = chr(123)  # '{'
rcb = chr(125)  # '}'

# Modification AK
def init_web_app(pool):
    global web_app
    web_app = Server(pool, "/static", debug=True)  # Serve from static directory
    setup_routes()
    return web_app

def setup_routes():
    @web_app.route("/edit/<filename>")
    def edit(request, filename):
        print("Editing ", filename)
        f = open(filename,"r",encoding='utf-8')
        textbuffer = ''
        for line in f:
            textbuffer = textbuffer + line
        f.close()
        response = edit_html.format(lcb, rcb, filename, textbuffer)
        return Response(request, response, content_type="text/html")
    
    # Modification AK
    @web_app.route("/view/<filename>")
    def view(request, filename):
        print("Editing ", filename)
        f = open(filename,"r",encoding='utf-8')
        textbuffer = ''
        for line in f:
            textbuffer = textbuffer + line
        f.close()
        response = view_html.format(lcb, rcb, filename, textbuffer, filename)
        return Response(request, response, content_type="text/html")

    # Test on Pico W 2022 saves file but makes webserver unresponsive
    @web_app.route("/write/<filename>",methods=["POST"])
    def write_script(request, filename):
        # Modification AK
        data = request.body.decode('utf-8')  # Convert bytes to string
        fields = data.split("&")
        form_data = {}
        for field in fields:
            key,value = field.split('=')
            form_data[key] = value

        storage.remount("/",readonly=False)
        f = open(filename,"w",encoding='utf-8')
        textbuffer = form_data['scriptData']
        textbuffer = cleanup_text(textbuffer)
        for line in textbuffer:
            f.write(line)
        f.close()
        print("Wrote script " + filename)
        # Modification AK
        response = ducky_main("Wrote script " + filename)
        return Response(request, response, content_type="text/html")

    # Test on Pico W 2022 saves file but makes webserver unresponsive
    @web_app.route("/new",methods=['GET','POST'])
    def write_new_script(request):
        response = ''
        if(request.method == 'GET'):
            response = new_html
        else:
            # Modification AK
            data = request.body.decode('utf-8')  # Convert bytes to string
            fields = data.split("&")
            form_data = {}
            for field in fields:
                key,value = field.split('=')
                form_data[key] = value
            filename = form_data['scriptName']
            textbuffer = form_data['scriptData']
            textbuffer = cleanup_text(textbuffer)
            storage.remount("/",readonly=False)
            f = open(filename,"w",encoding='utf-8')
            for line in textbuffer:
                f.write(line)
            f.close()
            print("Wrote script " + filename)
            # Modification AK
            response = ducky_main("Wrote script " + filename)
        return Response(request, response, content_type="text/html")

    @web_app.route("/run/<filename>")
    def run_script(request, filename):
        print("run_script ", filename)
        # Modification AK
        response = ducky_main("Running script " + filename)
        runScript(filename)
        return Response(request, response, content_type="text/html")

    # Modification AK
    @web_app.route("/")
    def index(request):
        response = ducky_main("")
        return Response(request, response, content_type="text/html")

    # Modification AK
    @web_app.route("/api", POST,append_slash=True)
    def api(request: Request):
        if request.method == POST :
            req = request.json()
            payload = req["content"]
            payload = payload.splitlines()
            exe(payload)
            response = ducky_main("Running custom script")
            return Response(request, response, content_type="text/html")

# Modification AK
payload_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Script-Type" content="text/javascript" />
    <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico  WIFI-Duck</title>
    <style>
        footer {}
            background-color: #2f3136;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        {}
        .form, form {}
            height: auto;
            width: 400px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        {}
    </style>
    <script>
        function sendHttpRequest(data) {}
        console.log(data);
        var url = "http://192.168.4.1/api" ;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.setRequestHeader("Content-Type", "application/json");
    
        xhr.onreadystatechange = function () {}
        if (xhr.readyState === XMLHttpRequest.DONE) {}
            if (xhr.status === 200) {}
            // Request was successful
            console.log("Request sent successfully!");
            {} else {}
            // Request failed
            console.error("Request failed. Status:", xhr.status);
            {}
        {}
        {};
    
        xhr.send(JSON.stringify(data));
        {};
        function main(){}
            var payload = document.getElementById("payload").value ;
            var data = {}username : "Payload" , content : payload{} ;
            sendHttpRequest(data) ;
        {}
    </script> 
</head>
<body>
  <div class="title">
      <h1>Pico WiFi Duck</h1>
  </div>
  <div class="form">
      {}
  </div>
  <div class="form">
      <table border="1"> <tr><th>Payload</th><th>Actions</th></tr> {} </table>
  </div>
  <div class="form">
      <h1>Custom Script Editor <a class="reload" id="editorReload"></a></h1>
      <textarea id="payload" name="content" placeholder="Enter text here..."></textarea>
      <button onclick="main()">RUN</button>
  </div>
  <!--
  <div class="form">
      <br>
      <button onclick="window.location.href='/new'">New Script</button>
      <a href="/new">New Script</a>
  </div>
  -->
  <footer style="background-color: #2f3136; color: white; text-align: center; padding: 10px;">
      Pico WiFi Ducky
  </footer>
</body>
</html>
"""

edit_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Script-Type" content="text/javascript" />
    <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico  WIFI-Duck</title>
    <style>
        footer {}
            background-color: #2f3136;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        {}
    </style>
</head>
<body>
    <h1>Pico WiFi Ducky</h1>
    <form action="/write/{}" method="POST">
        <textarea rows="5" cols="60" name="scriptData">{}</textarea>
        <br/>
        <input type="submit" value="submit"/>
    </form>
    <br>
    <button onclick="window.location.href='/'">Home</button>
    <footer style="background-color: #2f3136; color: white; text-align: center; padding: 10px;">
        Pico WiFi Ducky
    </footer>
</body>
</html>
"""
# Modification AK
view_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Script-Type" content="text/javascript" />
    <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico  WIFI-Duck</title>
    <style>
        footer {}
            background-color: #2f3136;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        {}
    </style>
</head>
<body>
    <h1>Pico WiFi Ducky</h1>
    <div class="form">
        <h1>View {}<a class="reload" id="editorReload"></a></h1>
        <textarea rows="5" cols="60" name="scriptData" readonly>{}</textarea>
        <button onclick="window.location.href='/run/{}'">Run</button>
    </div>
    <br>
    <button onclick="window.location.href='/'">Home</button>
    <footer style="background-color: #2f3136; color: white; text-align: center; padding: 10px;">
        Pico WiFi Ducky
    </footer>
</body>
</html>
"""

new_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Script-Type" content="text/javascript" />
    <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico  WIFI-Duck</title>
    <style>
        footer {}
            background-color: #2f3136;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        {}
    </style>
</head>
<body>
    <h1>Pico WiFi Ducky</h1>
    <form action="/new" method="POST">
        Script Name<br>
        <textarea rows="1" cols="60" name="scriptName"></textarea>
        Script<br>
        <textarea rows="5" cols="60" name="scriptData"></textarea>
        <br/>
        <input type="submit" value="submit"/>
    </form>
    <br>
    <button onclick="window.location.href='/'">Home</button>
    <footer style="background-color: #2f3136; color: white; text-align: center; padding: 10px;">
        Pico WiFi Ducky
</footer>
</body>
</html>
"""

response_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="x-dns-prefetch-control" content="off">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="Content-Script-Type" content="text/javascript" />
    <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
    <meta name="mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico  WIFI-Duck</title>
    <style>
        footer {}
            background-color: #2f3136;
            color: white;
            text-align: center;
            padding: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
        {}
    </style>
</head>
<body>
    <h1>Pico WiFi Ducky</h1>
    {}
    <br>
    <button onclick="window.location.href='/'">Home</button>
    <footer style="background-color: #2f3136; color: white; text-align: center; padding: 10px;">
        Pico WiFi Ducky
    </footer>
</body>
</html>
"""

# Modification AK
newrow_html = "<tr><td>{}</td><td><button onclick=""window.location.href='/view/{}'"">View</button> / <button onclick=""window.location.href='/run/{}'"">Run</button></tr>"

# Test on Pico W 2022 saves file but makes webserver unresponsive
#newrow_html = "<tr><td>{}</td><td><button onclick=""window.location.href='/edit/{}'"">Edit</button> / <button onclick=""window.location.href='/run/{}'"">Run</button></tr>"

def setPayload(payload_number):
    if(payload_number == 1):
        payload = "payload.dd"

    else:
        payload = "payload"+str(payload_number)+".dd"

    return(payload)


def ducky_main(status):
    print("Ducky main")
    payloads = []
    rows = ""
    files = os.listdir()
    #print(files)
    for f in files:
        if ('.dd' in f) == True:
            payloads.append(f)
            newrow = newrow_html.format(f,f,f)
            #print(newrow)
            rows = rows + newrow
    
    # Modification AK
    response = payload_html.format(lcb, rcb, lcb, rcb, lcb, lcb, lcb, lcb, rcb, lcb, rcb, rcb, rcb, rcb, lcb, lcb, rcb, rcb, status, rows)

    return(response)

_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def cleanup_text(string):
    """unquote('abc%20def') -> b'abc def'."""
    global _hextobyte

    if not string:
        return b''

    if isinstance(string, str):
        string = string.encode('utf-8')

    bits = string.split(b'%')
    if len(bits) == 1:
        return string

    res = [bits[0]]
    append = res.append

    if _hextobyte is None:
        _hextobyte = {(a + b).encode(): bytes([int(a + b, 16)])
                      for a in _hexdig for b in _hexdig}

    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]])
            append(item[2:])
        except KeyError:
            append(b'%')
            append(item)

    return b''.join(res).decode().replace('+',' ')

# Modification AK
# Global variable to keep track of the server task
server_task = None

async def startWebService():
    global server_task
    if server_task is not None:
        # If the server is already running, cancel the existing task
        server_task.cancel()
        await server_task  # Wait for the task to finish

    # Start the web server
    server_task = asyncio.create_task(web_app.serve_forever('192.168.4.1', 80))
    print("Web service started.")
