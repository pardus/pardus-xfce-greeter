# Pardus Welcome

Pardus Welcome is a greeter application that welcomes the user after login.

It is currently a work in progress. Maintenance is done by <a href="https://www.pardus.org.tr/">Pardus</a> team.

[![Packaging status](https://repology.org/badge/vertical-allrepos/pardus-welcome.svg)](https://repology.org/project/pardus-welcome/versions)

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
git clone https://github.com/pardus/pardus-welcome.git ~/pardus-welcome
```

Run application
```bash
python3 ~/pardus-welcome/src/Main.py
```

### **Build deb package**

```bash
sudo apt install devscripts git-buildpackage
sudo mk-build-deps -ir
gbp buildpackage --git-export-dir=/tmp/build/pardus-welcome -us -uc
```

### **Screenshots**

![Pardus Welcome 1](screenshots/pardus-welcome-1.png)

![Pardus Welcome 2](screenshots/pardus-welcome-2.png)

![Pardus Welcome 3](screenshots/pardus-welcome-3.png)

![Pardus Welcome 4](screenshots/pardus-welcome-4.png)
