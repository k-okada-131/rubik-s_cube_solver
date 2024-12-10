#include "cube.h"

namespace rubik_cube{
    Cube moves[COUNT_CUBE_PH1];
    
    void corner::mul(const Cube& c1, const Cube& move, Cube& into) {
        for (int i = 0; i < corner::COUNT; i++) {
            into.cp[i] = c1.cp[move.cp[i]];
            into.co[i] = (c1.co[move.cp[i]] + move.co[i]) % 3;
        }
    }

    void edge::mul(const Cube& c1, const Cube& move, Cube& into) {
        for (int i = 0; i < edge::COUNT; i++) {
            into.ep[i] = c1.ep[move.ep[i]];
            into.eo[i] = (c1.eo[move.ep[i]] + move.eo[i]) % 2;
        }
    }

    void mul(const Cube& c1, const Cube& c2, Cube& into) {
        corner::mul(c1, c2, into);
        edge::mul(c1, c2, into);
    }

    void init(){
        Cube base_moves[] = {
            { // U
                {3, 0, 1, 2, 4, 5, 6, 7},
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
            }, { // D
                {0, 1, 2, 3, 5, 6, 7, 4},
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
            }, { // R
                {0, 2, 6, 3, 4, 1, 5, 7},
                {0, 1, 2, 0, 0, 2, 1, 0},
                {0, 5, 9, 3, 4, 2, 6, 7, 8, 1, 10, 11},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
            }, { // L
                {4, 1, 2, 0, 7, 5, 6, 3},
                {2, 0, 0, 1, 1, 0, 0, 2},
                {11, 1, 2, 7, 4, 5, 6, 0, 8, 9, 10, 3},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
            }, { // F
                {0, 1, 3, 7, 4, 5, 2, 6},
                {0, 0, 1, 2, 0, 0, 2, 1},
                {0, 1, 6, 10, 4, 5, 3, 7, 8, 9, 2, 11},
                {0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0}
            }, { // B
                {1, 5, 2, 3, 0, 4, 6, 7},
                {1, 2, 0, 0, 2, 1, 0, 0},
                {4, 8, 2, 3, 1, 5, 6, 7, 0, 9, 10, 11},
                {1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0}
            }};

        for (int ax = 0, i = 0; ax < 3; ax++) {
            int f1 = 2 * ax;
            int f2 = f1 + 1;
            int off1 = 15 * ax;
            int off2 = off1 + 3;

            moves[i] = base_moves[f1];
            mul(moves[i], base_moves[f1], moves[i + 1]); // 180°
            mul(moves[i + 1], base_moves[f1], moves[i + 2]); // 270°
            // 対面
            i += 3;
            moves[i] = base_moves[f2];
            mul(moves[i], base_moves[f2], moves[i + 1]);
            mul(moves[i + 1], base_moves[f2], moves[i + 2]);
            // 同時操作
            i += 3;
            for (int cnt1 = 0; cnt1 < 3; cnt1++) {
                for (int cnt2 = 0; cnt2 < 3; cnt2++)
                    mul(moves[off1 + cnt1], moves[off2 + cnt2], moves[i++]);
            }
        }
    }
}