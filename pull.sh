#!/bin/bash

git pull
git submodule sync --recursive
git submodule update --init --remote --recursive