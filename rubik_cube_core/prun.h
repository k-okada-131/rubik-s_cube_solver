#ifndef _PRUN_H_
#define _PRUN_H_

#include "cube.h"
#include "stdio.h"
#include <cstdlib>

namespace rubik_cube{

    const int NUM_CO = 2187; // 3 ** 7
    const int NUM_EO = 2048; // 2 ** 11
    const int NUM_E_COMBINATIONS = 495; // 12C4
    const int NUM_CP = 40320; // 8!
    const int NUM_UD_EP = 40320; // 8!
    const int NUM_E_EP = 24; // 4!

    extern int co_move_table[NUM_CO][COUNT_CUBE_PH1];
    extern int eo_move_table[NUM_CO][COUNT_CUBE_PH1];
    extern int e_combination_table[NUM_E_COMBINATIONS][COUNT_CUBE_PH1];
    extern int cp_move_table[NUM_CP][COUNT_CUBE_PH2];
    extern int ud_ep_move_table[NUM_UD_EP][COUNT_CUBE_PH2];
    extern int e_ep_move_table[NUM_E_EP][COUNT_CUBE_PH2];
    extern int co_eec_prune_table[NUM_CO][NUM_E_COMBINATIONS];
    extern int eo_eec_prune_table[NUM_EO][NUM_E_COMBINATIONS];
    extern int cp_eep_prune_table[NUM_CP][NUM_E_EP];
    extern int udep_eep_prune_table[NUM_UD_EP][NUM_E_EP];

    void createTables();
    void create_move_tables_ph1();
    void create_move_tables_ph2();
    void create_prune_tables_ph1();
    void create_prune_tables_ph2();

    // Phase 1
    inline int co_to_index(const int* co){
        int index = 0;
        for(int i = 0; i < corner::COUNT - 1; i++){
            index *= 3;
            index += co[i];
        }
        return index;
    }

    inline void index_to_co(int* co, int index){
        int sum_co = 0;
        for(int i = 6; i > -1; i--){
            co[i] = index % 3;
            index /= 3;
            sum_co += co[i];
        }
        co[corner::COUNT-1] = (3 - sum_co % 3) % 3;
    }

    inline int eo_to_index(const int* eo){
        int index = 0;
        for(int i = 0; i < edge::COUNT - 1; i++){
            index *= 2;
            index += eo[i];
        }
        return index;
    }

    inline void index_to_eo(int* eo, int index){
        int sum_eo = 0;
        for(int i = 10; i > -1; i--){
            eo[i] = index % 2;
            index /= 2;
            sum_eo += eo[i];
        }
        eo[edge::COUNT-1] = (2 - sum_eo % 2) % 2;
    }
    // nCrを計算
    inline int calc_combination(int n, int r){
        int ret = 1;
        for(int i = 0; i < r; i++){
            ret *= (n - i);
        }
        for(int i = 0; i < r; i++){
            ret /= (r - i);
        }
        return ret;
    }

    inline int e_combination_to_index(const int* comb){
        int index = 0;
        int r = 4;
        for(int i = edge::COUNT - 1; i > -1; i--){
            if(comb[i]){
                index += calc_combination(i, r);
                r -= 1;
            }
        }
        return index;
    }

    inline void index_to_e_combination(int* combination, int index){
        int r = 4;
        for(int i = edge::COUNT - 1; i > -1; i--){
            if(index >= calc_combination(i, r)){
                combination[i] = 1;
                index -= calc_combination(i, r);
                r -= 1;
            }
        }
    }

    // Phase 2
    inline int cp_to_index(const int* cp){
        int index = 0;
        for(int i = 0; i < corner::COUNT - 1; i++){
            index *= 8 - i;
            for(int j = i + 1; j < 8; j++){
                if(cp[i] > cp[j])
                    index++;
            }
        }
        return index;
    }

    inline void index_to_cp(int* cp, int index){
        for(int i = 6; i > -1; i--){
            cp[i] = index % (8 - i);
            index /= 8 -i;
            for(int j = i + 1; j < 8; j++){
                if(cp[j] >= cp[i])
                    cp[j]++;
            }
        }
    }

    inline int ud_ep_to_index(const int* ep){
        int index = 0;
        int offset = 4; // 前半4つは考慮しない
        int udep_count = 8; // 後半8つを計算
        for(int i = 0; i < udep_count; i++){
            index *= udep_count - i;
            for(int j = i + 1; j < udep_count; j++){
                if(ep[i + offset] > ep[j + offset])
                    index++;
            }
        }
        return index;
    }

    inline void index_to_ud_ep(int* ep, int index){
        int offset = 4; // 前半4つは考慮しない
        int udep_count = 8; // 後半8つを計算
        for(int i = 0; i  < offset; i++)
            ep[i] = 0;
        for(int i = udep_count - 2; i > -1; i--){
            ep[i + offset] = index % (udep_count - i);
            index /= udep_count - i;
            for(int j = i + 1; j < udep_count; j++){
                if(ep[j + offset] >= ep[i + offset])
                    ep[j + offset]++;
            }
        }
    }

    inline int e_ep_to_index(const int* eep){
        int index = 0;
        int eep_count = 4; // 前半4つを計算
        for(int i = 0; i < eep_count; i++){
            index *= eep_count - i;
            for(int j = i + 1; j < eep_count; j++){
                if(eep[i] > eep[j])
                    index++;
            }
        }
        return index;
    }

    inline void index_to_e_ep(int* eep, int index){
        int eep_count = 4; // 前半4つを計算
        for(int i = eep_count; i < edge::COUNT; i++)
            eep[i] = 0;
        for(int i = eep_count - 2; i > -1; i--){
            eep[i] = index % (eep_count - i);
            index /= eep_count - i;
            for(int j = i + 1; j < eep_count; j++){
                if(eep[j] >= eep[i])
                    eep[j]++;
            }
        }
    }
}

#endif