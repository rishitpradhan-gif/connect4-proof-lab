#ifndef SETTINGS_H_
#define SETTINGS_H_

#include <cstdint>

// Defines settings which can be tuned for the target machine and target problem.
// In rough order of importance.

// The shape of the board.
inline constexpr int BOARD_WIDTH = 9;
inline constexpr int BOARD_HEIGHT = 9;

// Enable/disable strong solutions:
//   * Weak solution: Will find if either player can force a win or if the game will be a draw after
//     perfect play. Does not give the move on which the game will end.
//
//   * Strong solution: Gives the weak solution plus the move on which the game will end assuming
//     perfect play. Slower than a weak solution, and requires more memory.
inline constexpr bool STRONG_SOLVES_ENABLED = false;

// Number of search threads. If 0, the number concurrent threads available on the machine is used.
inline constexpr int NUM_THREADS = 1;

// Full-key entries use 32 bytes on this 128-bit-board build.
// 524,309 entries require about 16 MiB per independent process.
inline constexpr uint64_t NUM_TABLE_ENTRIES = 524309;

// Enable 2 MB pages, instead of 4 KB. Not implemented for Macs.
inline constexpr bool ENABLE_HUGE_PAGES = false;

// Restrict each search thread to a single core. Only implemented on Windows.
inline constexpr bool ENABLE_AFFINITY = false;

// At depths higher than this value, the search will do a transposition table
// lookup for each child in hope of tightening bounds or finding a cut off.
inline constexpr int ENHANCED_TABLE_CUTOFF_PLIES = BOARD_WIDTH * BOARD_HEIGHT - 15;

// Determines how much noise to add to move scores near the root of the search tree
// when searching with multiple threads. This noise helps threads to desync.
// Only used when running with more than one search thread.
inline constexpr float MOVE_SCORE_JITTER = 0.3f;

// Whether an opening book should be read into the transposition table before solving any positions.
inline constexpr bool LOAD_BOOK_FILE = false;

// Table files contain significant results (nodes with millions of child nodes) which are used to
// speed up future runs. These settings control the use of these files.
inline constexpr unsigned long long MIN_NODES_FOR_TABLE_FILE = 1 * 1000 * 1000;
inline constexpr bool LOAD_TABLE_FILE = true;
inline constexpr bool UPDATE_TABLE_FILE = true;

static_assert(!(LOAD_BOOK_FILE && LOAD_TABLE_FILE), "Cannot load an opening book and a table file.");

#endif
