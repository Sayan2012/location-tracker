import subprocess
import re

def start_tunnel():
    process = subprocess.Popen(
        ["cloudflared.exe", "tunnel", "--url", "http://localhost:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Read lines until the public URL is found
    for line in process.stdout:
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            return match.group(0)
    
    return None
