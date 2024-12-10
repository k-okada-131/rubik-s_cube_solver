#include "cube.h"
#include "prun.h"
#include "search.h"
#include "socket_server.h"
#include <ctime>
#include <stdio.h>

/*
    ロボットのサーバ側
    コンパイル
    g++ -O2 cube.cpp prun.cpp search.cpp socket_server.cpp main.cpp -lwsock32 -o main

    実行
    ./main.exe [max_solution_length]
    max_solution_length 許容解の長さ(短すぎると時間がかかるか見つからない)
*/

using namespace rubik_cube;

int main(int argc, char* argv[]){
    init();
    createTables();

    Socket sock = Socket();
    srand((unsigned)time(NULL));
    int max_solution_length = 18;
    if(argc >= 2)
		max_solution_length = atoi(argv[1]);
    
    int* ans;
    ans = (int*)malloc(sizeof(int) * max_solution_length);

    Cube cube;
    bool found;
    printf("Setup Finish\n");
    while(true){
        sock.sock_recv(cube);
        Search search(max_solution_length);
        if(search.start_search(cube)){
            int solution_length = search.get_solution(ans);
            printf("Ans = ");
            std::string ans_str = "";
            for(int i = 0;i<solution_length;i++){
                ans_str += moves_name[ans[i]];
            }
            sock.sock_send(ans_str);
            printf("%s(%d moves)\n", ans_str.c_str(), solution_length);
            FILE* fp = fopen("solution_log.txt", "a+");
            fprintf(fp, "%s\n", ans_str.c_str());
            fclose(fp);
        }
        else{
            printf("Ans not found\nCP : ");
            for(int i = 0; i < corner::COUNT; i++)
                printf("%d ", cube.cp[i]);
            printf("\nCO");
            for(int i = 0; i < corner::COUNT; i++)
                printf("%d ", cube.co[i]);
            printf("\nEP");
            for(int i = 0; i < edge::COUNT; i++)
                printf("%d ",cube.ep[i]);
            printf("\nEO");
            for(int i = 0; i < edge::COUNT; i++)
                printf("%d ", cube.eo[i]);
            printf("\n");
            break;
        }
    }
    return 0;
}