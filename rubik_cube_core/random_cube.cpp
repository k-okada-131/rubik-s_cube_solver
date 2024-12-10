#include "cube.h"
#include "prun.h"
#include "search.h"
#include <ctime>

/*
   コンパイル
   g++ -O2 cube.cpp prun.cpp search.cpp random_cube.cpp -o random

   実行
   ./main.exe [N] [max_solution_length]
   N ランダムキューブを解く回数
   max_solution_length 許容解の長さ(短すぎると時間がかかるか見つからない)
*/

using namespace rubik_cube;

int main(int argc, char* argv[]){
    init();
    createTables();

    srand((unsigned)time(NULL));
    int N = 100;
    int max_solution_length = 18;
    if(argc > 1)
		N = atoi(argv[1]);
    if(argc > 2)
		max_solution_length = atoi(argv[2]);
    Cube cube = {{0, 1, 2, 3, 4, 5, 6, 7},{0, 0, 0, 0, 0, 0, 0, 0},{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11},{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}}; // 初期状態
    Cube tmp_cube;
    int* ans;
    ans = (int*)malloc(sizeof(int) * max_solution_length);
    clock_t start, end;
    float solution_time, time_sum = 0;
    float length_sum = 0;
    for(int i = 0; i < N; i++){
        Search search(max_solution_length);
        for(int move_i = 0; move_i < 15; move_i++){
            mul(cube,moves[rand() % 45],tmp_cube);
            cube = tmp_cube;
        }
        start = clock();
        bool found = search.start_search(cube);
        end = clock();
        solution_time = (float)(end - start) / CLOCKS_PER_SEC * 1000;
        time_sum += solution_time;
        if(found){
            int solution_length = search.get_solution(ans);
            printf("Ans = ");
            for(int i = 0;i<solution_length;i++){
                printf("%s",moves_name[ans[i]].c_str());
            }
            length_sum += solution_length;
            printf(" (%d moves, %.1f ms)\n",solution_length, solution_time);
        }
    }
    free(ans);
    printf("-----------------Results-----------------\n");
    printf("N = %d, max_solution_length = %d\n", N, max_solution_length);
    printf("Solve time average = %f ms\n", time_sum / N);
    printf("Solve length average = %f moves\n", length_sum / N);
}