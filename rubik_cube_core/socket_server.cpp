#include "socket_server.h"

// g++ .\socket_server.cpp -lwsock32
namespace rubik_cube{
    Socket::Socket(){
        WSAStartup(MAKEWORD(2,0), &data);

        memset(&srcAddr, 0, sizeof(srcAddr));
        srcAddr.sin_port = htons(PORT);
        srcAddr.sin_family = AF_INET;
        srcAddr.sin_addr.s_addr = htonl(INADDR_ANY);

        // ソケット生成(ストリーム)
        srcSocket = socket(AF_INET, SOCK_STREAM, 0);
        // バインド
        bind(srcSocket, (struct sockaddr *) &srcAddr, sizeof(srcAddr));
        listen(srcSocket, 1);
    }

    void Socket::sock_recv(Cube& cube){
        while(1){
            // printf("waiting...\n");
            dstSocket = accept(srcSocket, (struct sockaddr *) &dstAddr, &dstAddrSize);
            // printf("connect -> %s\n", inet_ntoa(dstAddr.sin_addr));

            numrcv = recv(dstSocket, buffer, sizeof(char)*128, 0);
            if(numrcv ==0 || numrcv ==-1 ){
                status = closesocket(dstSocket); break;
            }
            buffer[numrcv] = '\0';
            str = buffer;
            if(sscanf(str.c_str(), "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d",
                &cube.cp[0], &cube.cp[1], &cube.cp[2], &cube.cp[3], &cube.cp[4], &cube.cp[5], &cube.cp[6], &cube.cp[7],
                &cube.co[0], &cube.co[1], &cube.co[2], &cube.co[3], &cube.co[4], &cube.co[5], &cube.co[6], &cube.co[7],
                &cube.ep[0], &cube.ep[1], &cube.ep[2], &cube.ep[3], &cube.ep[4], &cube.ep[5], &cube.ep[6], &cube.ep[7], &cube.ep[8], &cube.ep[9], &cube.ep[10], &cube.ep[11],
                &cube.eo[0], &cube.eo[1], &cube.eo[2], &cube.eo[3], &cube.eo[4], &cube.eo[5], &cube.eo[6], &cube.eo[7], &cube.eo[8], &cube.eo[9], &cube.eo[10], &cube.eo[11]
                ) != edge::COUNT*2 + corner::COUNT*2)
            {
                printf("data false: %s\n", str.c_str());
            }
            return;
        }
    }

    void Socket::sock_send(std::string data){
        send(dstSocket, data.c_str(), sizeof(char)*data.size(), 0);
        while(1){
            if(numrcv ==0 || numrcv ==-1 )
                closesocket(dstSocket); break;
        }
    }   
}