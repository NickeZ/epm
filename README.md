# EPM

EPM helps you compile and maintain your epics installation.

# Install

It is recommended to install EPM with PIP.

## Dependencies

EPM is compatible with both python >=2.7 and >=3.4

### Ubuntu 16.04

```bash
sudo apt install python3-pip git
```

## With PIP in your home directory

```bash
pip3 install --user git+https://github.com/NickeZ/epm.git
```

Add the PIP bin dir to your bashrc:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
source $HOME/.bashrc
```

## With PIP system wide

```bash
sudo pip3 install git+https://github.com/NickeZ/epm.git
```

# Usage

```bash
epm --help
```
