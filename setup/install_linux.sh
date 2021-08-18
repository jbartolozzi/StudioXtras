#!/usr/bin/env bash
USER_BAK=${USER}
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}
INSTALL_DIR=$(realpath "../StudioXtras/python2.7libs/StudioXtras")
sudo ln -s "${INSTALL_DIR}" "/home/${USER_BAK}/houdini18.5/python2.7libs/StudioXtras"