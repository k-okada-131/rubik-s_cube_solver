#ifndef _SEARCH_H_
#define _SEARCH_H_

#include "prun.h"
#include <vector>
#include <thread>

namespace rubik_cube{
    class Search{
        public:
            Search(int max_length){
                max_solution_length = 9999;
                
                max_solution_length = max_length;
                best_solution = (int*)malloc(sizeof(int)*max_solution_length);
            };

            ~Search(){
                free(best_solution);
            };

            bool start_search(Cube cube);

            int get_solution(int* solution){
                for(int i = 0; i < max_solution_length; i++){
                    solution[i] = best_solution[i];
                }
                return max_solution_length;
            };
            int max_solution_length;

        private:
            bool start_phase1();
            void timer();
            bool start_phase2(Cube state);
            bool depth_limited_search_ph1(int co_index, int eo_index, int e_comb_index, int depth);
            bool depth_limited_search_ph2(int cp_index, int udep_index, int eep_index, int depth);
            inline bool is_move_available(int prev_move, int move){ 
                if(prev_move == -1)
                    return true;
                return int(prev_move / 15) != int(move / 15);
            };
            Cube initial_state;
            std::vector<int> current_solution_ph1;
            std::vector<int> current_solution_ph2;
            int* best_solution;
            int* moves_ph1;
            int* moves_ph2;
            float solve_time;
            bool timeout_flag;
    };
}

#endif