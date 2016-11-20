# EPM

EPM helps you compile and maintain your epics installation.

# Install

It is recommended to install EPM with PIP.

## Dependencies

EPM is compatible with both python >=2.7 and >=3.4

### Ubuntu 16.04

```bash
sudo apt install python3-pip git
echo 'PATH="$HOME/.local/bin:$PATH"' >> $HOME/.profile
source $HOME/.profile
```

### CentOS 7

```bash
sudo yum install epel-release git
sudo yum install python34-setuptools
sudo easy_install-3.4 pip
sed -i 's|$PATH:$HOME/.local/bin:$HOME/bin|$HOME/.local/bin:$HOME/bin:$PATH|' $HOME/.bash_profile
```

## Single user (~/.local/bin)

```bash
pip3 install --user git+https://github.com/NickeZ/epm.git
```

## System wide (/usr/local/bin)

```bash
sudo pip3 install git+https://github.com/NickeZ/epm.git
```

# Usage

```bash
epm --help
```
