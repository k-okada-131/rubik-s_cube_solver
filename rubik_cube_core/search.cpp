#include "search.h"
#include <cassert>

namespace rubik_cube{
    bool Search::start_search(Cube cube){
        initial_state = cube;
        return start_phase1();
    }

    bool Search::start_phase1(){
        int co_index = co_to_index(initial_state.co);
        int eo_index = eo_to_index(initial_state.eo);
        int e_combination[edge::COUNT];
        for(int i = 0; i < edge::COUNT; i++)
            e_combination[i] = initial_state.ep[i] < 4? 1: 0;
        int e_comb_index = e_combination_to_index(e_combination);
        int depth = 0;
        while(depth <= max_solution_length){
            if(depth_limited_search_ph1(co_index, eo_index, e_comb_index, depth)){
                return true;
            }
            depth++;
        }
        return false;
    }

    // 返り値 -1:強制終了 0:未発見 1:発見
    bool Search::start_phase2(Cube state){
        int cp_index = cp_to_index(state.cp);
        int udep_index = ud_ep_to_index(state.ep);
        int eep_index = e_ep_to_index(state.ep);
        int depth = 0;
        while(depth <= max_solution_length - current_solution_ph1.size()){
            if(depth_limited_search_ph2(cp_index, udep_index, eep_index, depth)) return true;
            depth++;
        }
        return false;
    }

    bool Search::depth_limited_search_ph1(int co_index, int eo_index, int e_comb_index, int depth){
        if(depth == 0 & co_index == 0 & eo_index == 0 & e_comb_index == 0){
            Cube state = initial_state;
            Cube tmp_state;
            for(int i = 0; i < current_solution_ph1.size(); i++){
                mul(state, moves[moves1[current_solution_ph1.at(i)]], tmp_state);
                state = tmp_state;
            }
            assert(co_to_index(state.co) == 0);
            assert(co_to_index(state.eo) == 0);
            return start_phase2(state);
        }
        if(depth == 0) return false;
        if(co_eec_prune_table[co_index][e_comb_index] > depth | eo_eec_prune_table[eo_index][e_comb_index] > depth) return false;
        int prev_move = -1;
        if(!current_solution_ph1.empty())
            prev_move = current_solution_ph1.back();
        for(int i = 0; i < COUNT_CUBE_PH1; i++){

            if(!is_move_available(prev_move, moves1[i])) continue;
            current_solution_ph1.push_back(moves1[i]);
            // 動作テーブルの参照はPH1操作番号の0~44のインデックス(not 操作番号)
            int next_co_index = co_move_table[co_index][i];
            int next_eo_index = eo_move_table[eo_index][i];
            int next_c_comb_index = e_combination_table[e_comb_index][i];
            if(depth_limited_search_ph1(next_co_index, next_eo_index, next_c_comb_index, depth - 1))
                return true;
            current_solution_ph1.pop_back();

        }
        return false;
    }

    bool Search::depth_limited_search_ph2(int cp_index, int udep_index, int eep_index, int depth){
        if(depth == 0 & cp_index == 0 & udep_index == 0 & eep_index == 0){
            max_solution_length = current_solution_ph1.size() + current_solution_ph2.size();
            int idx = 0;
            for(int i = 0; i < current_solution_ph1.size(); i++, idx++){
                best_solution[idx] = current_solution_ph1.at(i);
            }   
            for(int i = 0; i < current_solution_ph2.size(); i++, idx++)
                best_solution[idx] = current_solution_ph2.at(i);
            return true;
        }
        if(depth == 0) return false;
        if(cp_eep_prune_table[cp_index][eep_index] > depth | udep_eep_prune_table[udep_index][eep_index] > depth) return false;

        int prev_move;
        if(!current_solution_ph2.empty()) prev_move = current_solution_ph2.back();
        else if(!current_solution_ph1.empty()) prev_move = current_solution_ph1.back();
        else prev_move = -1;

        for(int i = 0; i < COUNT_CUBE_PH2; i++){
            if(!is_move_available(prev_move, moves2[i])) continue;
            current_solution_ph2.push_back(moves2[i]);
            // 動作テーブルの参照はPH2操作番号の0~20のインデックス(not 操作番号)
            int next_cp_index = cp_move_table[cp_index][i];
            int next_udep_index = ud_ep_move_table[udep_index][i];
            int next_eep_index = e_ep_move_table[eep_index][i];
            if(depth_limited_search_ph2(next_cp_index, next_udep_index, next_eep_index, depth - 1)) 
                return true;
            current_solution_ph2.pop_back();
        }
        return false;
    }
}