#include "ft_malcolm.h"

static void fillstruct_arp(t_arp *pkt)
{
    pkt->frame_type = htons(0x0806);
    pkt->hw_type = htons(ETHER_HW_TYPE);
    pkt->prot_type = htons(0x0800);
    pkt->hw_addr_size = ETHMACADDRLEN;
    pkt->prot_addr_size = IPADDRLEN;
    pkt->op = htons(2);
}

void        fillpkt_arp(char *const *argv, t_arp *pkt, struct sockaddr *sa, char *ifa)
{
    struct in_addr  src;
    struct in_addr  tgt;

    parsemacaddr((char*)pkt->tgt_hw_addr, argv[4]);
    parsemacaddr((char*)pkt->rcpt_hw_addr, argv[4]);
    parsemacaddr((char*)pkt->src_hw_addr,  argv[2]);
    parsemacaddr((char*)pkt->sndr_hw_addr, argv[2]);
    parseipaddr(&src,  argv[1]);
    parseipaddr(&tgt, argv[3]);
    ft_memcpy(pkt->sndr_ip_addr, &src,  IPADDRLEN);
    ft_memcpy(pkt->rcpt_ip_addr, &tgt, IPADDRLEN);
    ft_bzero(pkt->padding, 18);
    ft_strcpy(sa->sa_data, ifa);
    fillstruct_arp(pkt);
}

int         getpkt_arp()
{
	int             ans;
    struct ethhdr   *eth;
    t_arph          *arp;
    
    ft_bzero(&g_gl.rcpkt, sizeof(g_gl.rcpkt));
	ans = recvfrom(g_gl.rsock, &g_gl.rcpkt, sizeof(g_gl.rcpkt), 0, NULL, NULL);
    eth = (struct ethhdr*)g_gl.rcpkt;
    arp = (t_arph*)(g_gl.rcpkt + 14);
    if (ans <= 0)
        return (-1);
    if (htons(eth->h_proto) == 0x0806)
    {  
        if (htons(arp->arp_op) == 0x0001)
        {
            printf("An ARP request has been broadcast.\n");
            printf("\tmac address of request: %02x:%02x:%02x:%02x:%02x:%02x\n", arp->arp_sha[0], arp->arp_sha[1], arp->arp_sha[2], arp->arp_sha[3], arp->arp_sha[4], arp->arp_sha[5]);
            printf("\tIP address of request: %02d.%02d.%02d.%02d\n", arp->arp_spa[0], arp->arp_spa[1], arp->arp_spa[2], arp->arp_spa[3]);
            return (1);
        }
    }
	return (-1);
}