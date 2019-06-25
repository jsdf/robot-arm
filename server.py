import socket 

import time
import BaseHTTPServer
import re
import os
from urlparse import urlparse
from urllib import unquote
import json
import math

script_dir = os.path.dirname(os.path.realpath(__file__))
initial_positions_file = os.path.join(script_dir, 'initialpositions.jsonc')

HOST_NAME = re.findall(r'inet addr:(\S+) ',os.popen("ifconfig wlan0").read())[0]
PORT_NUMBER = 8080

print_debug_data = True

arm_ranges =[
  ["7", 150, 300, 500], # rotate base (mid=300)
  ["8", 150, 300, 500], # arm bottom joint  (mid=300)
  ["10", 150, 320, 500], # arm middle joint (mid=320)
  ["11", 150, 300, 500], # tilt claw (min=150, mid=300, max=500)
  ["13", 150, 300, 500], # rotate claw (mid=300)
  ["15", 150, 300, 500]  # close claw (mid=300)
]

def write_positions(plan_servo):
    f= open("positions.json","w+")
    f.write(json.dumps(plan_servo))
    f.close()

def read_positions(source_file):
    with open(source_file, 'r') as content_file:
        content = content_file.read()
    return json.loads(re.sub(r'\/\/.*\n','',content))


# reset to default position
# initial_positions = read_positions(initial_positions_file)
# write_positions(initial_positions)


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Access-Control-Allow-Origin", "*")
        if s.path.startswith("/move"):
            s.send_header("Content-type", "application/json")
            s.end_headers()

            plan_rad = json.loads(unquote(urlparse(s.path).query))["plan"]

            plan_servo = {}
            debug_items = []
            
            for i, rad_str in enumerate(plan_rad):
                print("i: "+str(i))
                rad_num =float(rad_str)
                deg = math.degrees(rad_num)
                # if arm_ranges[i][0] == "7": # wrap rotation
                #     rad_num = rad_num  % (2*math.pi)
                if arm_ranges[i][0] == "8": # motor on pin 8 moves backwards
                    rad_num *= -1
                norm =rad_num / math.pi * 2
                base = arm_ranges[i][2]
                half_range = arm_ranges[i][2] - arm_ranges[i][1]
                for_servo = int(base + (half_range) * (norm) )
                # clamp
                for_servo = max(min(for_servo, arm_ranges[i][3]), arm_ranges[i][1])

                pin = arm_ranges[i][0]

                debug = {"pin":pin, "rad":rad_num, "deg":deg, "norm": norm, "base": base, "half_range": half_range, "for_servo": for_servo}
                if print_debug_data:
                    print(json.dumps(debug))
                plan_servo[pin] = for_servo
                debug_items.append(debug)
            print(json.dumps(plan_servo))
            write_positions(plan_servo)
            
            s.wfile.write(json.dumps({"output": plan_servo, "debug": debug_items}))
        else:
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write("<html><head><title>Title goes here.</title></head>")
            s.wfile.write("<body><p>This is a test.</p>")
            # If someone went to "http://something.somewhere.net/foo/bar/",
            # then s.path equals "/foo/bar/".
            s.wfile.write("<p>You accessed path: %s</p>" % s.path)
            s.wfile.write("</body></html>")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)