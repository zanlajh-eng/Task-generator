import os
import sys
import subprocess
import shutil

def get_resource_path(relative_path):
    """ Dobi pot do datoteke znotraj EXE-ja ali v mapi. """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 1. Poiščemo vgrajen HTML
source_html = get_resource_path("campaign-task-generator.html")

# 2. Prepišemo ga v lokalno mapo, kjer je EXE (da ga Edge vidi)
# To reši napako "Datoteke ni mogoče najti"
target_html = os.path.join(os.getcwd(), "view_generator.html")
try:
    shutil.copy(source_html, target_html)
except:
    pass # Če že obstaja, gremo naprej

# 3. Zaženemo Edge v varnem načinu
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = "msedge"

cmd = [
    edge_path,
    f"--app=file:///{target_html}",
    "--disable-web-security", # To je ključno za Google Sheets!
    "--user-data-dir=C:/temp_edge_generator"
]

subprocess.Popen(cmd)