#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <cstring>
#include <random>

namespace fs = std::filesystem;

/* ===================== CONFIG ===================== */

#define SECRET_KEY "bashquest_internal_secret"
#define CONFIG_DIR ".config/bashquest"

/* ===================== STATE ===================== */

struct State {
    uint32_t challenge;     // current challenge (1-based)
    uint64_t flag_hash;     // hash of expected flag
    uint32_t checksum;      // integrity check
    char workspace[512];    // absolute path to workspace
};

uint32_t simple_hash(const State& s) {
    uint32_t h = 5381;
    const char* k = SECRET_KEY;
    while (*k)
        h = ((h << 5) + h) ^ *k++;

    h ^= s.challenge;
    h ^= s.flag_hash;
    for (char c : s.workspace)
        h ^= c;

    return h;
}

fs::path state_dir() {
    const char* home = std::getenv("HOME");
    if (!home) {
        std::cerr << "HOME not set\n";
        std::exit(1);
    }
    fs::path p(home);
    p /= CONFIG_DIR;
    return p;
}

bool load_state(State& s) {
    std::ifstream f(state_dir() / "state.bin", std::ios::binary);
    if (!f)
        return false;
    f.read(reinterpret_cast<char*>(&s), sizeof(s));
    return s.checksum == simple_hash(s);
}

void save_state(const State& s) {
    State copy = s;
    copy.checksum = simple_hash(copy);
    fs::create_directories(state_dir());
    std::ofstream f(state_dir() / "state.bin", std::ios::binary);
    f.write(reinterpret_cast<const char*>(&copy), sizeof(copy));
}

/* ===================== UTIL ===================== */

void make_writable_recursive(const fs::path& p) {
    if (!fs::exists(p)) return;

    // First, make directory itself writable
    if (fs::is_directory(p)) {
        fs::permissions(p, fs::perms::owner_all | fs::perms::group_all | fs::perms::others_all,
                        fs::perm_options::replace);
        for (auto& entry : fs::directory_iterator(p)) {
            make_writable_recursive(entry.path());
        }
    } else {
        // Regular file: make writable
        fs::permissions(p, fs::perms::owner_all | fs::perms::group_all | fs::perms::others_all,
                        fs::perm_options::replace);
    }
}

void reset_workspace(const fs::path& ws) {
    if (fs::exists(ws)) {
        make_writable_recursive(ws);  // ensure deletion is possible
        fs::remove_all(ws);
    }

    fs::create_directories(ws);  // recreate workspace
}
void mkdir(const fs::path& p) {
    fs::create_directory(p);
}

/* ===================== RANDOM HELPERS ===================== */

const std::vector<std::string> short_names = {
    "bin","lib","src","tmp","var",
    "log","opt","dev","etc","run"
};

const std::vector<std::string> long_names = {
    "extraordinarily_long_directory_name",
    "another_unnecessarily_verbose_directory",
    "final_directory_that_you_should_autocomplete",
    "ridiculously_specific_and_annoying_directory_name",
    "this_directory_name_is_way_too_long"
};

std::string random_from(const std::vector<std::string>& v) {
    return v[std::rand() % v.size()];
}

/* ===================== CHALLENGE 1 ===================== */

void setup_challenge_1(State& state) {
    fs::path ws = fs::absolute("workspace");
    reset_workspace(ws);

    std::string d1 = random_from(short_names);
    std::string d2 = random_from(short_names);
    std::string d3 = random_from(short_names);

    mkdir(ws / d1);
    mkdir(ws / d1 / d2);
    mkdir(ws / d1 / d2 / d3);

    state.challenge = 1;
    state.flag_hash = std::hash<std::string>{}(d3);
    std::strncpy(state.workspace, ws.c_str(), sizeof(state.workspace) - 1);
    save_state(state);

    std::cout << "Challenge 1:\n";
    std::cout << "Three directories were created, one inside another.\n";
    std::cout << "Find the deepest one. The flag is its name.\n";
}

bool check_challenge_1(const State& state, const std::string& flag) {
    return std::hash<std::string>{}(flag) == state.flag_hash;
}

/* ===================== CHALLENGE 2 ===================== */

void setup_challenge_2(State& state) {
    fs::path ws = fs::path(state.workspace);
    reset_workspace(ws);

    std::string d1 = long_names[0];
    std::string d2 = long_names[1];
    std::string d3 = long_names[2];

    mkdir(ws / d1);
    mkdir(ws / d1 / d2);
    mkdir(ws / d1 / d2 / d3);

    state.challenge = 2;
    state.flag_hash = std::hash<std::string>{}(d3);
    save_state(state);

    std::cout << "Challenge 2:\n";
    std::cout << "Same task, but directory names are painful to type.\n";
    std::cout << "Use tab completion.\n";
}

bool check_challenge_2(const State& state, const std::string& flag) {
    return std::hash<std::string>{}(flag) == state.flag_hash;
}

/* ===================== CHALLENGE 3 ===================== */

// TODO: generarare i nomi di directory a caso

void setup_challenge_3(State& state) {
    // Workspace path (same as existing workspace)
    fs::path ws = fs::absolute("workspace");
    reset_workspace(ws);

    // Level 1
    fs::path start = ws / "start";
    mkdir(start);

    // Level 2 (two options)
    fs::path go_left  = start / "go_left";
    fs::path go_right = start / "go_right";
    mkdir(go_left);
    mkdir(go_right);

    // Level 3
    fs::path treasure = go_left / "treasure";   // correct path
    fs::path deadend  = go_right / "deadend";   // decoy
    mkdir(treasure);
    mkdir(deadend);

    // Store flag in state (deepest directory name)
    state.challenge = 3;
    state.flag_hash = std::hash<std::string>{}("treasure"); // flag = "treasure"
    std::strncpy(state.workspace, ws.c_str(), sizeof(state.workspace) - 1);
    save_state(state);

    // Instructions
    std::cout << "Challenge 3 (CD mastery):\n";
    std::cout << "Navigate the directory maze using 'cd' to reach the hidden treasure.\n";
    std::cout << "Only by moving step by step can you reach the deepest directory.\n";
}

bool check_challenge_3(const State& state, const std::string& flag) {
    return std::hash<std::string>{}(flag) == state.flag_hash;
}

/* ===================== CHALLENGE 4 ===================== */

// Helper to generate random directory names
std::string random_dirname(size_t len = 6) {
    static const char charset[] =
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    static std::mt19937 rng(std::time(nullptr));
    static std::uniform_int_distribution<> dist(0, sizeof(charset) - 2);
    std::string s;
    for (size_t i = 0; i < len; ++i)
        s += charset[dist(rng)];
    return s;
}

// L'albero non può essere listato grazie al settaggio dei permessi
// Il file .txt nelle directory deve essere aperto con cat
// contiene il nome della directory successiva in cui fare cd
//
// Cannot be solved with ls, ls -R, or tree
// Requires cd and cat
// Is discoverable but not guessable
// Uses random directory names
// Uses correct Unix permission semantics
// Is portable and deterministic

void setup_challenge_4(State& state) {
    fs::path ws = fs::absolute("workspace");
    reset_workspace(ws);

    std::string d1 = random_dirname();
    std::string d2 = random_dirname();
    std::string d3 = random_dirname(); // flag

    fs::path p1 = ws / d1;
    fs::path p2 = p1 / d2;
    fs::path p3 = p2 / d3;

    fs::create_directory(p1);
    fs::create_directory(p2);
    fs::create_directory(p3);

    // Instruction files
    {
        std::ofstream(p1 / "INSTRUCTIONS.txt")
            << "To continue, cd into:\n" << d2 << "\n";
        std::ofstream(p2 / "INSTRUCTIONS.txt")
            << "To continue, cd into:\n" << d3 << "\n";
        std::ofstream(p3 / "INSTRUCTIONS.txt")
            << "You reached the deepest directory.\n"
               "The directory name is the flag.\n"
               "Use pwd to show the full path.\n";
    }

    auto x = fs::perms::owner_exec |
             fs::perms::group_exec |
             fs::perms::others_exec;

    auto r = fs::perms::owner_read |
             fs::perms::group_read |
             fs::perms::others_read;

    // Directories: --x (no listing!)
    fs::permissions(p1, x, fs::perm_options::replace);
    fs::permissions(p2, x, fs::perm_options::replace);
    fs::permissions(p3, x, fs::perm_options::replace);

    // Instruction files: r--
    fs::permissions(p1 / "INSTRUCTIONS.txt", r, fs::perm_options::replace);
    fs::permissions(p2 / "INSTRUCTIONS.txt", r, fs::perm_options::replace);
    fs::permissions(p3 / "INSTRUCTIONS.txt", r, fs::perm_options::replace);

    state.challenge = 4;
    state.flag_hash = std::hash<std::string>{}(d3);
    std::strncpy(state.workspace, ws.c_str(), sizeof(state.workspace) - 1);
    save_state(state);

    std::cout << "Challenge 4 (permissions + cd):\n";
    std::cout << "You cannot list directories.\n";
    std::cout << "Read INSTRUCTIONS.txt and use 'cd'.\n";
    std::cout << "The flag is the deepest directory name.\n";
    std::cout << "Use pwd anytime to show the current path.\n";
}

bool check_challenge_4(const State& state, const std::string& flag) {
    return std::hash<std::string>{}(flag) == state.flag_hash;
}

/* ===================== MAIN ===================== */

int main(int argc, char* argv[]) {
    std::srand(std::time(nullptr));

    if (argc < 2) {
        std::cout << "Usage: bashquest start | submit FLAG | reset\n";
        return 0;
    }

    std::string cmd = argv[1];
    State state{};

    if (!load_state(state)) {
        state.challenge = 1;
        state.flag_hash = 0;
        state.workspace[0] = '\0';
        save_state(state);
    }

    if (cmd == "reset") {
        make_writable_recursive(state_dir());
        make_writable_recursive("workspace");

        fs::remove_all(state_dir());
        fs::remove_all("workspace");

        std::cout << "Progress reset.\n";
        return 0;
    }

    if (cmd == "start") {
        setup_challenge_1(state);
        return 0;
    }

    if (cmd == "submit") {
        if (argc < 3) {
            std::cout << "Missing flag.\n";
            return 1;
        }

        std::string flag = argv[2];
        bool ok = false;

        if (state.challenge == 1)
            ok = check_challenge_1(state, flag);
        else if (state.challenge == 2)
            ok = check_challenge_2(state, flag);
        else if (state.challenge == 3)
            ok = check_challenge_3(state, flag);
        else if (state.challenge == 4)
            ok = check_challenge_4(state, flag);
        else {
            std::cout << "All challenges completed.\n";
            return 0;
        }

        if (!ok) {
            std::cout << "Wrong flag.\n";
            return 1;
        }

        std::cout << "Correct!\n";
        state.challenge++;
        save_state(state);

        if (state.challenge == 2)
            setup_challenge_2(state);
        else if (state.challenge == 3)
            setup_challenge_3(state);
        else if (state.challenge == 4)
            setup_challenge_4(state);
        else
            std::cout << "You completed all challenges.\n";

        return 0;
    }

    std::cout << "Unknown command.\n";
    return 0;
}
