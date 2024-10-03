#!/bin/bash

git pull
git submodule sync --recursive
git submodule update --init --remote --recursive
git submodule foreach 'git checkout main || echo "Failed to checkout main in $name"; git pull origin main'
