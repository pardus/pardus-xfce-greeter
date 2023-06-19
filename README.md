# Pardus Xfce Greeter

Pardus Xfce Greeter is a greeter application that welcomes the user after login.

It is currently a work in progress. Maintenance is done by <a href="https://www.pardus.org.tr/">Pardus</a> team.

[![Packaging status](https://repology.org/badge/vertical-allrepos/pardus-xfce-greeter.svg)](https://repology.org/project/pardus-xfce-greeter/versions)

### **Dependencies**

This application is developed based on Python3 and GTK+ 3. Dependencies:
```bash
gir1.2-glib-2.0 gir1.2-gtk-3.0 python3-gi python3
```

### **Run Application from Source**

Install dependencies
```bash
sudo apt install gir1.2-glib-2.0 gir1.2-gtk-3.0 python3-gi python3
```

Clone the repository
```bash
git clone https://github.com/pardus/pardus-xfce-greeter.git ~/pardus-xfce-greeter
```

Run application
```bash
python3 ~/pardus-xfce-greeter/src/Main.py
```

### **Build deb package**

```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pardus-xfce-greeter -us -uc
```

### **Screenshots**

![Pardus Greeter 1](screenshots/pardus-xfce-greeter-1.png)

![Pardus Greeter 2](screenshots/pardus-xfce-greeter-2.png)

![Pardus Greeter 3](screenshots/pardus-xfce-greeter-3.png)

![Pardus Greeter 4](screenshots/pardus-xfce-greeter-4.png)
