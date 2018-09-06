g++ src/driver_display_callback.cpp -o driver_display_callback.so -Wall -O2 -shared -fPIC \
-I/home/lvxejay/development/opt/env/arnold/include \
-L/home/lvxejay/development/opt/env/arnold/bin -lai -Wl,-rpath="/home/lvxejay/development/opt/env/arnold/bin"