#!/bin/bash
[ -d reborn ] || git submodule add -b develop https://gitlab.com/kirianlab/reborn
git submodule update --init --recursive --remote

