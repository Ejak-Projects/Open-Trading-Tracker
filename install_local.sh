#!/bin/bash

echo "================================================="
echo " Building and installing Open Trading Tracker... "
echo "================================================="

# Compile and install using pacman automatically
makepkg -si --noconfirm

echo "================================================="
echo " Installation Complete! "
echo " You can now launch 'Open Trading Tracker' from "
echo " your desktop environment's application menu. "
echo "================================================="
