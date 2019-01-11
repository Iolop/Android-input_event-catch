#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/limits.h>
#include <poll.h>
#include <sys/poll.h>
#include <errno.h>
#include <unistd.h>
#include <linux/input.h>

int main(int argc,char*argv[])
{
    int keylog = open("/sdcard/CATCH_EVENT",O_CREAT|O_RDWR);
    int *deviceFd = (int*)malloc(sizeof(int)*(argc-1));
    int i = 0;
    int trueDevice = 0;
    int res = 0;
    struct input_event test;
    printf("input_event size: %d\n",sizeof(test));
    printf("input_event.time size: %d\n",sizeof(test.time));
    printf("input_event.type size: %d\n",sizeof(test.type));
    printf("input_event.code size: %d\n",sizeof(test.code));
    printf("input_event.value size: %d\n",sizeof(test.value));
//search all argv[*] find device could open
	for (i=1;i<argc;i++){
		int tmp = open(argv[i],O_RDWR);
		if(tmp>0){
			deviceFd[trueDevice] = tmp;
			trueDevice++;
		}
	}  

    struct pollfd* fds = (struct pollfd*)malloc(sizeof(struct pollfd)*trueDevice);
    for (i=0;i<trueDevice;i++){
		fds[i].fd = deviceFd[i];
		fds[i].events = POLLIN ;
    }
    while(1){
	struct input_event event_in;
	int pollres = poll(fds,trueDevice,-1);
	for(i=0;i<trueDevice;i++){
	    res = read(fds[i].fd,&event_in,sizeof(event_in));
	    if(res<sizeof(event_in))
			continue;
	    //if(event_in.type != EV_ABS)
		//continue;
	    else if(event_in.type == EV_ABS || event_in.type == EV_SYN){
		printf("%x %x %x\n",event_in.type,event_in.code,event_in.value);
	    	write(keylog,&event_in,sizeof(event_in));
	    }
	}
    }
}

