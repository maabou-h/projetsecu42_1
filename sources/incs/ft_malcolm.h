#ifndef _FT_MALCOLM_H
# define _FT_MALCOLM_H

# include <stdio.h>
# include <signal.h>
# include <ctype.h>
# include <stdlib.h>
# include <unistd.h>
# include <string.h>
# include <errno.h>
# include <netdb.h>
# include <sys/socket.h>
# include <arpa/inet.h>
# include <ifaddrs.h>
# include <linux/if_ether.h>
# include <linux/if_packet.h>
# include <linux/if_arp.h>

# include "libft.h"

# define ETHMACADDRLEN 6
# define IPADDRLEN     4
# define ETHER_HW_TYPE   1

char usage[] = {
  "ft_malcolm\n\
  \tusage: ft_malcolm interface src-ip src-mac prey-ip prey-mac\n\n"
};

typedef struct                          s_gl
{
  char                                  rcpkt[4096];
  int                                   sock;
  int                                   rsock;
}                                       t_gl;

typedef struct __attribute__((packed))  s_arp
{
  unsigned char                         tgt_hw_addr[ETHMACADDRLEN];
  unsigned char                         src_hw_addr[ETHMACADDRLEN];
  unsigned short                        frame_type;
  unsigned short                        hw_type;
  unsigned short                        prot_type;
  unsigned char                         hw_addr_size;
  unsigned char                         prot_addr_size;
  unsigned short                        op;
  unsigned char                         sndr_hw_addr[ETHMACADDRLEN];
  unsigned char                         sndr_ip_addr[IPADDRLEN];
  unsigned char                         rcpt_hw_addr[ETHMACADDRLEN];
  unsigned char                         rcpt_ip_addr[IPADDRLEN];
  unsigned char                         padding[18];
}                                       t_arp;

typedef struct __attribute__((packed))  s_arph
{
    unsigned short                      arp_hd;
    unsigned short                      arp_pr;
    unsigned char                       arp_hdl;
    unsigned char                       arp_prl;
    unsigned short                      arp_op;
    unsigned char                       arp_sha[6];
    unsigned char                       arp_spa[4];
    unsigned char                       arp_dha[6];
    unsigned char                       arp_dpa[4];
}                                       t_arph;

#endif