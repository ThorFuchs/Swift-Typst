#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    if (mount("proc", "/proc", "proc", 0, NULL) != 0) {
        perror("mount /proc");
        return 1;
    }
    puts("SWIFT_TYPST_CONSUMER_BEGIN");
    fflush(stdout);
    pid_t child = fork();
    if (child == 0) {
        execl("/Consumer", "Consumer", (char *)NULL);
        perror("exec");
        _exit(127);
    }
    int status = 0;
    if (child < 0 || waitpid(child, &status, 0) < 0) {
        perror("wait");
        status = 127 << 8;
    }
    printf("SWIFT_TYPST_CONSUMER_EXIT=%d\n",
           WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status));
    fflush(stdout);
    sync();
    reboot(RB_POWER_OFF);
    for (;;) pause();
}
