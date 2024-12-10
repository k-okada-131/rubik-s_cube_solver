#include "prun.h"
#include "stdio.h"

namespace rubik_cube{
    
    int co_move_table[NUM_CO][COUNT_CUBE_PH1];
    int eo_move_table[NUM_CO][COUNT_CUBE_PH1];
    int e_combination_table[NUM_E_COMBINATIONS][COUNT_CUBE_PH1];
    int cp_move_table[NUM_CP][COUNT_CUBE_PH2];
    int ud_ep_move_table[NUM_UD_EP][COUNT_CUBE_PH2];
    int e_ep_move_table[NUM_E_EP][COUNT_CUBE_PH2];
    int co_eec_prune_table[NUM_CO][NUM_E_COMBINATIONS];
    int eo_eec_prune_table[NUM_EO][NUM_E_COMBINATIONS];
    int cp_eep_prune_table[NUM_CP][NUM_E_EP];
    int udep_eep_prune_table[NUM_UD_EP][NUM_E_EP];

    void create_move_tables_ph1(){
        Cube tmp_cube;
        Cube cube = {
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};
        // coの遷移表作成 45手 * 2187(3**7)パターン
        for(int i = 0; i < NUM_CO; i++){
            int co[corner::COUNT];
            memset(co, 0, sizeof(co));
            index_to_co(co, i);
            cube.set_co(co);
            for(int move_num = 0; move_num < COUNT_CUBE_PH1; move_num++){
                mul(cube, moves[move_num], tmp_cube);
                co_move_table[i][move_num] = co_to_index(tmp_cube.co);
            }
        }
        // eoの遷移表作成 45手 * 2048(2**11)パターン
        for(int i = 0; i < NUM_EO; i++){
            int eo[edge::COUNT];
            memset(eo, 0, sizeof(eo));
            index_to_eo(eo, i);
            cube.set_eo(eo);
            for(int move_num = 0; move_num < COUNT_CUBE_PH1; move_num++){
                mul(cube, moves[move_num], tmp_cube);
                eo_move_table[i][move_num] = eo_to_index(tmp_cube.eo);
            }
        }
        // E列エッジの組み合わせの遷移表 45手 * 495(12C4)パターン
        for(int i = 0; i < NUM_E_COMBINATIONS; i++){
            int eco[edge::COUNT];
            memset(eco, 0, sizeof(eco));
            index_to_e_combination(eco, i);
            cube.set_ep(eco);
            for(int move_num = 0; move_num < COUNT_CUBE_PH1; move_num++){
                mul(cube, moves[move_num], tmp_cube);
                e_combination_table[i][move_num] = e_combination_to_index(tmp_cube.ep);
            }
        }
    }

    void create_move_tables_ph2(){
        Cube tmp_cube;
        Cube cube = {
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
                {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}};
        // cpの遷移表 21手 * 40320(8!)パターン
        for(int i = 0; i < NUM_CP; i++){
            int cp[corner::COUNT];
            memset(cp, 0, sizeof(cp));
            index_to_cp(cp, i);
            cube.set_cp(cp);
            for(int move_num = 0; move_num < COUNT_CUBE_PH2; move_num++){
                mul(cube, moves[moves2[move_num]], tmp_cube);
                cp_move_table[i][move_num] = cp_to_index(tmp_cube.cp);
            }
        }
        // UD面エッジのEPの遷移表 21手 * 40320(8!)パターン
        for(int i = 0; i < NUM_UD_EP; i++){
            int ep[edge::COUNT];
            memset(ep, 0, sizeof(ep));
            index_to_ud_ep(ep, i);
            cube.set_ep(ep);
            for(int move_num = 0; move_num < COUNT_CUBE_PH2; move_num++){
                mul(cube, moves[moves2[move_num]], tmp_cube);
                ud_ep_move_table[i][move_num] = ud_ep_to_index(tmp_cube.ep);
            }
        }
        // E列エッジのEPの遷移表 21手 * 24(4!)パターン
        int eep[edge::COUNT];
        for(int i = 0; i < NUM_E_EP; i++){
            memset(eep, 0, sizeof(eep));
            index_to_e_ep(eep, i);
            cube.set_ep(eep);
            for(int move_num = 0; move_num < COUNT_CUBE_PH2; move_num++){
                mul(cube, moves[moves2[move_num]], tmp_cube);
                e_ep_move_table[i][move_num] = e_ep_to_index(tmp_cube.ep);
            }
        }
    }

    void create_prune_tables_ph1(){
        memset(co_eec_prune_table, -1, sizeof(co_eec_prune_table));
        co_eec_prune_table[0][0] = 0;
        int distance = 0;
        int num_failed = 1;
        int next_co, next_eec;
        while(num_failed != NUM_CO * NUM_E_COMBINATIONS){
            for(int i_co = 0; i_co < NUM_CO; i_co++){
                for(int i_eec = 0; i_eec < NUM_E_COMBINATIONS; i_eec++){
                    if(co_eec_prune_table[i_co][i_eec] == distance){
                        for(int i_move = 0; i_move < COUNT_CUBE_PH1; i_move++){
                            next_co = co_move_table[i_co][i_move];
                            next_eec = e_combination_table[i_eec][i_move];
                            if(co_eec_prune_table[next_co][next_eec] == -1){
                                co_eec_prune_table[next_co][next_eec] = distance + 1;
                                num_failed++;
                            }
                        }
                    }
                }
            }
            distance++;
        }
        memset(eo_eec_prune_table, -1, sizeof(eo_eec_prune_table));
        eo_eec_prune_table[0][0] = 0;
        distance = 0;
        num_failed = 1;
        int next_eo;
        while(num_failed != NUM_EO * NUM_E_COMBINATIONS){
            for(int i_eo = 0; i_eo < NUM_EO; i_eo++){
                for(int i_eec = 0; i_eec < NUM_E_COMBINATIONS; i_eec++){
                    if(eo_eec_prune_table[i_eo][i_eec] == distance){
                        for(int i_move = 0; i_move < COUNT_CUBE_PH1; i_move++){
                            next_eo = eo_move_table[i_eo][i_move];
                            next_eec = e_combination_table[i_eec][i_move];
                            if(eo_eec_prune_table[next_eo][next_eec] == -1){
                                eo_eec_prune_table[next_eo][next_eec] = distance + 1;
                                num_failed++;
                            }
                        }
                    }
                }
            }
            distance++;
        }
    }

    void create_prune_tables_ph2(){
        memset(cp_eep_prune_table, -1, sizeof(cp_eep_prune_table));
        cp_eep_prune_table[0][0] = 0;
        int distance = 0;
        int num_failed = 1;
        int next_cp, next_eep;
        while(num_failed != NUM_CP * NUM_E_EP){
            for(int i_cp = 0; i_cp < NUM_CP; i_cp++){
                for(int i_eep = 0; i_eep < NUM_E_EP; i_eep++){
                    if(cp_eep_prune_table[i_cp][i_eep] == distance){
                        for(int i_move = 0; i_move < COUNT_CUBE_PH2; i_move++){
                            next_cp = cp_move_table[i_cp][i_move];
                            next_eep = e_ep_move_table[i_eep][i_move];
                            if(cp_eep_prune_table[next_cp][next_eep] == -1){
                                cp_eep_prune_table[next_cp][next_eep] = distance + 1;
                                num_failed += 1;
                            }
                        }
                    }
                }
            }
            distance++;
        }
        memset(udep_eep_prune_table, -1, sizeof(udep_eep_prune_table));
        udep_eep_prune_table[0][0] = 0;
        distance = 0;
        num_failed = 1;
        int next_udep;
        while(num_failed != NUM_UD_EP * NUM_E_EP){
            for(int i_udep = 0; i_udep < NUM_UD_EP; i_udep++){
                for(int i_eep = 0; i_eep < NUM_E_EP; i_eep++){
                    if(udep_eep_prune_table[i_udep][i_eep] == distance){
                        for(int i_move = 0; i_move < COUNT_CUBE_PH2; i_move++){
                            next_udep = ud_ep_move_table[i_udep][i_move];
                            next_eep = e_ep_move_table[i_eep][i_move];
                            if(udep_eep_prune_table[next_udep][next_eep] == -1){
                                udep_eep_prune_table[next_udep][next_eep] = distance + 1;
                                num_failed += 1;
                            }
                        }
                    }
                }
            }
            distance++;
        }
    }

    void createTables(){
        printf("Start create_tables!\n");
        create_move_tables_ph1();
        printf("Finished create_move_tables_ph1!\n");
        create_move_tables_ph2();
        printf("Finished create_move_tables_ph2!\n");
        create_prune_tables_ph1();
        printf("Finished create_prune_tables_ph1!\n");
        create_prune_tables_ph2();
        printf("Finished create_prune_tables_ph2!\n");
    }

}