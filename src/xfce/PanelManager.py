import subprocess

def restoreDefaults():
    subprocess.run("xfce4-panel --quit; pkill xfconfd; rm -rf ~/.config/xfce4/panel ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml; (xfce4-panel &);", shell=True)