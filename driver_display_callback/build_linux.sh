# g++ src/driver_display_callback.cpp -o driver_display_callback.so -Wall -O2 -shared -fPIC \
# -I/home/lvxejay/development/opt/env/arnold/include \
# -L/home/lvxejay/development/opt/env/arnold/bin -lai -Wl,-rpath="/home/lvxejay/development/opt/env/arnold/bin"

# Remove the current addon
sudo rm -rf $HOME/bin/blender/v2.79b/2.79/scripts/addons/barnold/**
# Remove CMake Configuration
sudo rm -rf /home/lvxejay/development/opt/env/build/barnold/**
cd $ARNOLD_HOME/../build/barnold
# Build New Shared Library
cmake $ARNOLD_HOME/../barnold/driver_display_callback
make
make install
# Copy current addon to Blender
cd $HOME/development/opt/env/barnold
sudo cp -R ./2.79b/barnold $HOME/bin/blender/v2.79b/2.79/scripts/addons/
sudo cp ./bin/libbarnold_display_callback.so $ARNOLD_HOME/plugins/libbarnold_display_callback.so
cd -
