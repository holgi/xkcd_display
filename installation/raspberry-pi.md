Setting up a Raspberry Pi.md
============================

Currently I use an old [Raspberry Pi 1B+][rpi1b], but will switch to a
[Raspberry Pi ZeroW][ripzw] as soon as it will arrive. There are a lot of
really good tutorials on how to set up a Raspberry, and this writeup is just
to have a (hopefully) complete documentation for the xkcd display - and of
cause as a reference for myself.


### About this installation procedure

This is a "headless" setup instruction, derived from a guide on
[circuit basics][cbguide]. This means, no keyboard and / or monitor is
connected to the Raspberry but everything is done via [ssh][ssh] terminal
sessions. I will not go into detail on how to use ssh (especially on windows)
and assume you have some basic knowledge on using the command line.


### Note of caution

The Raspberry will be connected to a network for the install. While the setup
takes place, the Raspberry will be exposed with a default username and
password and accessible on the network for a brief period of time. But this
timespan will be enough for *everybody* - and I mean *worldwide* - if the
Raspberry is on a *public network* and not protected by a firewall.


Getting Raspbian on an SD card
------------------------------

First you need to download the latest "Raspbian Lite" [distribution][rplite]
and flash an SD card with the disk image. The method highly depends on the
operating system you are currently using - so there will be no detailed
instruction on this.

Before removing the SD card, you should add a file named `SSH` to the SD card's
root directory. Yes, the name is `SSH` without any extension like .txt or
any other. If this file is present on boot, the server side ssh daemon will be
launched as soon as the system has booted. If it's missing, you'd only be able
to login with an attached keyboard and monitor.

If you have a Raspberry Pi with WLAN and want to use it from the start - e.g.
on a Raspberry Pi Zero W - you need to add another file to the root folder of
the SD card. The file must be named `wpa_supplicant.conf` and the content
should be something like this:

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="test"
    psk="mypassword"
    key_mgmt=WPA-PSK
}
```

Of cause you should replace the value for `ssid` with the name of your WLAN and
the value of `psk` with the password of the connection.


First Boot
----------

Put the SD card in the Raspberry, add an ethernet cable and before powering up
read again the paragraph titled "Note of caution". Ready?

Try to find the IP address of the Raspberry. Since this depends on your network
setup there will be no further asistence to this task. But if you have an IPv6
enabled network, you could use the `ping6 -I eth0 ff02::1` command to find
other network nodes on your local network (you might need to substitute `eth0`
with the network interface on your local machine)

You should now be able to log in to the Raspberry with `ssh pi@<pi-ip-address>`.
(I will use the address 10.0.0.100 from now on for the Raspberry).It should ask
you, If you accept the presented ID, and propably you should or you won't be
able to log in. After the confirmation you can log in with the default password
`raspberry`  The first thing to do is to issue the command `sudo passwd pi` to
change the password of the current user. This step is the most important thing
to do to add some security to the Raspberry.


Adding a new user
-----------------

Since I don't like to work with the default user everybody knows, I'd recommend
to set up a new user:

 - `sudo useradd -m <username>` adds a new user and creates a home directory
 - `sudo passwd <username>` sets a password for the new user
 - `sudo usermod <username> -G sudo` adds the user to the group `sudo`. This
    enables the new user to issue commands with root privileges.

After adding the new user – let's cal her *jane* from now on - you should test
if you can log on to the Raspberry with the new account. So on your local
machine start a new ssh session with `ssh jane@10.0.0.100`. You should be abel
to log in with Jane's password. The next test would be if you can run a command
as root user: `sudo ls /`. This should prompt you once again for the password
and should work without an error.


More security (and convenience)
-------------------------------

Although generally speaking adding more security means less convenience,
sometimes there is an exception to this rule. With ssh you can use a private
key instead of a password to log in to the Raspberry Pi.

This new login procedure relies on public / private key cryptograpy. This topic
fills some books (propably a small library) if you want to go into detail.

The most importent thing is, that the private key is *a secret you have to
keep*. This file must not be exposed to the public. Don't share this file.
Don't copy it (except to your *encrypted* backup device). Don't show it to
anyone. Just don't. Never.

The other part is the public key. You can copy this around, even to other
servers and people and other people servers.

I won't fall down the rabbit hole on what the best parameters to use to create
the key pair and if you should use a password for the key file or not. I want
to keep it very simple.

If you have already a public / private key pair, you can skip the creation
and transfer of the key. You are not sure and use a Linux or Mac? Then you can
type `ls ~/.ssh` into the terminal on your local machine and if it shows you
some files like `id_rsa` and `id_rsa.pub`, you already have a key (and maybe
you should think about from where and why you got them).

Creating a key pair is quite simple (maybe not on Windows, I don't really know
that OS). Once again: only issue this command if you *don't have* a key pair
already - read the previous paragraph once again if you are not sure. On your
local machine type `ssh-keygen -o -b 4096 -t rsa` into your command prompt.

You now need to transfer the public key to the Raspberry. There is a very
convenient way to do this with `ssh-copy-id jane@10.0.0.100`. If you start a
new ssh session with `ssh jane@10.0.0.100` you should not be prompted for your
password.

The last thing todo on security is to disable a ssh login without a password.
After this step you must use public key authentication as described above. If
you mess something up, you'll still be able to log in to your Raspberry by
attaching a monitor and a keyboard. This is all done on your Rapsberry Pi, so
start a new ssh session if there is not already one open.

We need to edit the sshd config file - note the extra 'd' at the end of 'ssh' -
as root user: `sudoedit /etc/ssh/sshd_config`. Move down to the line
`#PubkeyAuthentication yes` and remove the pound sign, the line should be
`PubkeyAuthentication yes`.

Scroll further down to the line `#PasswordAuthentication yes`, again remove the
pound sign and change yes to no. The line should look this way:
`PasswordAuthentication no`

Probably the next line is `#PermitEmptyPasswords no`. Just remove the pound
sign so it looks like `PermitEmptyPasswords no`.

You can save the changes with `^o` (ctrl o) to write the changes back to disk.
This will show you a somewhat strange looking file name but don't be worried
about it. You can exit the editor with `^x` (ctrl x).

After the edit I'd recommend to check if the edits are really saved back. The
command `grep PasswordAuthentication /etc/ssh/sshd_config` should show you the
first edited line with no pound sign ('#') and no 'yes' in it.

We need to reload the changed configuration, but a note of caution here: If
something went wrong, there is a chance that you are not able to log in. I
would recommend to *not close* the current ssh session after issuing the
reload with `sudo service ssh reload`.

In a *new* terminal window try to connect to the Raspberry with the default
user: `ssh pi@10.0.0.100`. This should not ask you for a password and reject
the connection attempt right away. Also in a *new* session try to connect with
`ssh jane@10.0.0.100` and this should work like charm.


Basic configuration
-------------------

Now come some easy setup and configuration steps for the Raspberry. The command
for this is `sudo raspi-config`. It might be, that you need to issue it a
couple of times and there will be at least one reboot. The steps can be in any
order you like but I'd recommend the following:

 1. `Update` - this might take a while, but you'd get the newest version of the
    raspi-config tool
 1. `Boot Options > Desktop / CLI > Console`: You don't need to start a full
    fledged graphical desktop environment if no monitor is connected - at least
    I think so.
 1. `Localization options > Change Locale`: you first need to select the locales
    that should be installed and in the next step the one to use. I selected
    'en_US.UTF-8' since this is the same as on my local machine
 1. `Localization options > Change timezones`: your choice, you know where you
    live
 1. `Advanced options > Expand file system`: This will let you use all of
    memory of the SD card.

You'll be asked to reboot. I would do so, so the file system can be expanded to
use the whole SD card.


Updates, Updates, Updates
-------------------------

This might take a while, but I strongly advice to update the installed system
and components:

 1. `sudo apt-get update`: update the known software package list
 1. `sudo apt-get upgrade --with-new-pkgs`: upgrade all installed components
 1. `sudo apt-get autoclean`: cleanup the local package list
 1. `sudo apt-get autoremove`: remove installed components that are no longer
    required
 1. `sudo reboot`: Well, reboot the system


Finished!
---------

Phew. The basic Raspberry Pi setup is done. There was nothing specific for the
xkcd display in this so far. You can now install and use this thing for what
ever you like.


Addition: Getting Comfy
-----------------------

My favorite text editor for the command line (vim) is luckily just one install
away: `sudo apt-get install vim`.

I personally don't like the provided bash shell. I switched to zsh a couple of
years ago and want it also on my Raspberry. So why do I put this here in this
guide? Because I did a mistake that lead to reinstalling everything since I
didn't have a spare monitor and keyboard lying around. So see this as a
cautionary tale:

Installing zsh is quite easy: `sudo apt-get install zsh`. You can find the path
to the freshly installed shell by using `which zsh` - it should be something
like "/usr/bin/zsh". Changing the shell for the user is also just a command
away `sudo chsh -s <path/to/zsh> jane`.

And now to the part that bit me: Don't log out of the ssh session right now.
Start a new one with `ssh jane@10.0.0.100`. If this works, everything is fine.
I hade a typo in the path to zsh when issuing the "chsh" command, logged out
and was not able to ssh into my Raspberry any more, because it didn't find the
login shell. Stupid me. And yes, I know I could have typed something like
``sudo chsh -s `which zsh` jane`` in the first place but somehow I never
remember this by heart. *sigh*


[rpi1b]: https://www.raspberrypi.org/products/raspberry-pi-1-model-b-plus/
[ripzw]: https://www.raspberrypi.org/products/raspberry-pi-zero-w/
[cbguide]: https://www.circuitbasics.com/raspberry-pi-basics-setup-without-monitor-keyboard-headless-mode/
[ssh]: https://en.wikipedia.org/wiki/Secure_Shell
[rplite]: https://www.raspberrypi.org/downloads/raspbian/
