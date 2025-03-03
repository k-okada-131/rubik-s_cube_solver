#ifndef _CUBE_H_
#define _CUBE_H_

#include <string.h>
#include <string>

// キューブの状態定義
namespace rubik_cube{
    // 操作名{回転させる面}{回転量}に操作配列のインデックスを割当て
    // U1 → 上面90°(時計回りが正)
    // U2 → 上面180°
    // U3 → 上面-90°
    const int U1 = 0;
    const int U2 = 1;
    const int U3 = 2; 
    const int D1 = 3; 
    const int D2 = 4;
    const int D3 = 5;
    const int U1D1 = 6;
    const int U1D2 = 7;
    const int U1D3 = 8;
    const int U2D1 = 9;
    const int U2D2 = 10;
    const int U2D3 = 11;
    const int U3D1 = 12;
    const int U3D2 = 13;
    const int U3D3 = 14;
    const int R1 = 15;
    const int R2 = 16;
    const int R3 = 17;
    const int L1 = 18;
    const int L2 = 19;
    const int L3 = 20;
    const int R1L1 = 21;
    const int R1L2 = 22;
    const int R1L3 = 23;
    const int R2L1 = 24;
    const int R2L2 = 25;
    const int R2L3 = 26;
    const int R3L1 = 27;
    const int R3L2 = 28;
    const int R3L3 = 29;
    const int F1 = 30;
    const int F2 = 31;
    const int F3 = 32;
    const int B1 = 33;
    const int B2 = 34;
    const int B3 = 35;
    const int F1B1 = 36;
    const int F1B2 = 37;
    const int F1B3 = 38;
    const int F2B1 = 39;
    const int F2B2 = 40;
    const int F2B3 = 41;
    const int F3B1 = 42;
    const int F3B2 = 43;
    const int F3B3 = 44;
    // 各phaseで操作可能な操作の数
    const int COUNT_CUBE_PH1 = 45;
    const int COUNT_CUBE_PH2 = 21;
    // phase1で可能な操作
    const int moves1[] = {
        U1, U2, U3, D1, D2, D3, U1D1, U1D2, U1D3, U2D1, U2D2, U2D3, U3D1, U3D2, U3D3,
        R1, R2, R3, L1, L2, L3, R1L1, R1L2, R1L3, R2L1, R2L2, R2L3, R3L1, R3L2, R3L3,
        F1, F2, F3, B1, B2, B3, F1B1, F1B2, F1B3, F2B1, F2B2, F2B3, F3B1, F3B2, F3B3
    };
    // phase2で可能な操作
    const int moves2[] = {
        U1, U2, U3, D1, D2, D3, U1D1, U1D2, U1D3, U2D1, U2D2, U2D3, U3D1, U3D2, U3D3,
        R2, L2, R2L2, F2, B2, F2B2
    };
    // 操作名一覧
    const std::string moves_name[] = {
        "U1 ", "U2 ", "U3 ", "D1 ", "D2 ", "D3 ", "U1D1 ", "U1D2 ", "U1D3 ", "U2D1 ", "U2D2 ", "U2D3 ", "U3D1 ", "U3D2 ", "U3D3 ",
        "R1 ", "R2 ", "R3 ", "L1 ", "L2 ", "L3 ", "R1L1 ", "R1L2 ", "R1L3 ", "R2L1 ", "R2L2 ", "R2L3 ", "R3L1 ", "R3L2 ", "R3L3 ",
        "F1 ", "F2 ", "F3 ", "B1 ", "B2 ", "B3 ", "F1B1 ", "F1B2 ", "F1B3 ", "F2B1 ", "F2B2 ", "F2B3 ", "F3B1 ", "F3B2 ", "F3B3 "
    };
    // コーナーパーツの数
    namespace corner {
        const int COUNT = 8;
    };
    // エッジパーツの数
    namespace edge {
        const int COUNT = 12;
    }; 
    // キューブ構造体の定義
    struct Cube{
        int cp[corner::COUNT]; // コーナーパーツの位置：何番のパーツが何番の位置にいあるか 
        int co[corner::COUNT]; // コーナーパーツの向き：何番のパーツがどの向きを向いているか
        int ep[edge::COUNT]; // エッジパーツの位置：何番のパーツが何番の位置にいあるか
        int eo[edge::COUNT]; // エッジパーツの向き：何番のパーツがどの向きを向いているか
        // キューブの各状態配列を設定するための関数
        void set_cp(int* cp_){
            memcpy(cp, cp_, corner::COUNT*sizeof(int));
        }
        void set_co(int* co_){
            memcpy(co, co_, corner::COUNT*sizeof(int));
        }
        void set_ep(int* ep_){
            memcpy(ep, ep_, edge::COUNT*sizeof(int));
        }
        void set_eo(int* eo_){
            memcpy(eo, eo_, edge::COUNT*sizeof(int));
        }

    };
    // 状態配列を操作する関数
    namespace corner{
        void mul(const Cube& c1, const Cube& move, Cube& into);
    }
    namespace edge{
        void mul(const Cube& c1, const Cube& move, Cube& into);
    }
    void mul(const Cube& c1, const Cube& c2, Cube& into);

    extern Cube moves[COUNT_CUBE_PH1];

    void init();
}

#endif