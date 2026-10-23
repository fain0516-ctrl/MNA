#!/system/bin/sh
# S10+ (SM-G975N) thermal + CPU/GPU probe. Read-only. No root required.
echo "##### DEVICE INFO #####"
echo "model=$(getprop ro.product.model)"
echo "android=$(getprop ro.build.version.release)"
echo "build=$(getprop ro.build.display.id)"
echo ""
echo "##### THERMAL ZONE TYPES #####"
for z in /sys/class/thermal/thermal_zone*; do
  echo "$z = $(cat $z/type 2>/dev/null)"
done
echo ""
echo "##### THERMAL SERVICE (android HAL) #####"
dumpsys thermalservice 2>/dev/null
echo ""
echo "##### SAMPLING START (every 5s) #####"
N=60
I=0
while [ $I -lt $N ]; do
  echo "===== SAMPLE $I  $(date '+%H:%M:%S') ====="
  echo "[THERMAL milli-degC]"
  for z in /sys/class/thermal/thermal_zone*; do
    T=$(cat "$z/type" 2>/dev/null)
    V=$(cat "$z/temp" 2>/dev/null)
    echo "$T=$V"
  done
  echo "[CPUFREQ kHz]"
  for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
    echo "$(dirname $(dirname $c))=$(cat "$c" 2>/dev/null)"
  done
  echo "[GPU clock]"
  cat /sys/kernel/gpu/gpu_clock 2>/dev/null || cat /sys/class/kgsl/kgsl-3d0/gpuclk 2>/dev/null || echo "n/a"
  echo "[TOP cpu users]"
  top -n 1 -b -o PID,%CPU,NAME 2>/dev/null | head -n 12
  echo ""
  I=$((I+1))
  sleep 5
done
echo "##### DONE #####"
