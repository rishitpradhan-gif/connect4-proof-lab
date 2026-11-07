#!/bin/sh
set -eu
cd "$(dirname "$0")"
CXX=${CXX:-clang++}
oracle_flag=-DC4_DISABLE_PAIR_ORACLE
if [ "${ENABLE_PAIRING_ORACLE:-0}" = 1 ]; then oracle_flag=-DC4_ENABLE_PAIR_ORACLE; fi
for target in attempt validate; do
 "$CXX" -std=c++20 -O3 -DNDEBUG "$oracle_flag" -pthread -o "$target" "engine/src/$target.cpp" engine/src/solver/*.cpp engine/src/solver/parallel/*.cpp engine/src/solver/util/*.cpp
done
"$CXX" -std=c++20 -O3 -o horizon horizon.cpp
"$CXX" -std=c++20 -O3 -o validate-horizon validate-horizon.cpp

"$CXX" -std=c++20 -O3 -DNDEBUG -pthread -o dfpn dfpn.cpp engine/src/solver/position.cpp
