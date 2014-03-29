#!/usr/bin/env bash

TERM="xterm-color"
RED="\033[4;31m"
GREEN="\033[4;32m"
YELLOW="\033[4;33m"
BLUE="\033[4;34m"
RESETCOLOR="\033[0m" 

echo -e "${BLUE}Setting up the Firewall${RESETCOLOR}"

sudo cat > /etc/pf.anchors/com.label305.pf.rules <<"EOF"
# PF firewall anchor file
# http://blog.scottlowe.org/2013/05/15/using-pf-on-os-x-mountain-lion/

# Block 8080 for host3
block out proto { tcp, udp } from any to 46.19.218.5 port 8080

EOF

sudo cat > /etc/pf.anchors/com.label305.pf.conf <<"EOF"
anchor "com.label305.pf"
load anchor "com.label305.pf" from "/etc/pf.anchors/com.label305.pf.rules"
EOF

sudo cat >> /Library/LaunchDaemons/com.label305.pf.plist <<"EOF"
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE plist PUBLIC "-//Apple Computer/DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.label305.pf.plist</string>
        <key>Program</key>
        <string>/sbin/pfctl</string>
        <key>ProgramArguments</key>
        <array>
            <string>/sbin/pfctl</string>
            <string>-e</string>
            <string>-f</string>
            <string>/etc/pf.anchors/com.label305.pf.conf</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>ServiceDescription</key>
        <string>FreeBSD Packet Filter (pf) daemon</string>
  	    <key>StandardErrorPath</key>
		<string>/var/log/pf.log</string>
		<key>StandardOutPath</key>
		<string>/var/log/pf.log</string>
    </dict>
</plist>
EOF

echo -e "${GREEN}Done setting up the Firewall${RESETCOLOR}"

