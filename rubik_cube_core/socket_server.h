#include <stdio.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include "cube.h"

// g++ .\socket_server.cpp -lwsock32

namespace rubik_cube{
	#define PORT 8080
	
	class Socket{
		public:
			Socket();
			void sock_recv(Cube& cube);
			void sock_send(std::string data);
		private:
			int srcSocket;
			int dstSocket;

			struct sockaddr_in srcAddr;
			struct sockaddr_in dstAddr;
			int dstAddrSize = sizeof(dstAddr);
			int status;

			int numrcv;
			char buffer[1024];
			std::string str;

			WSADATA data;

	};

}
