# Packaging instruction

## Debian

```bash
# you should, must?, do everything in a VM in case there's some problems

# install build dependencies
apt install build-essential devscripts debhelper meson libglib2.0-dev

# get a dist from a release or whatever named 'stroked-{version}.tar.xz'

# rename it with:
# '-' is replaced by '_'
# add '.orig' before the first extension
mv stroked-{version}.tar.xz stroked_{version}.orig.tar.xz

# unpack it and cd into the unpacked directory
tar -xf stroked_{version}.orig.tar.xz
cd stroked-{version}

# run the thing
debuild -us -uc

# some errors later you should have a bunch of files in the parent folder
# you can try to install it with the .deb file by running:
sudo apt install ../stroked_{version}-1_all.deb

# if everything went ok you can now:
stroked

# will see for the next steps…
```

## Arch

```bash
# todo
```
