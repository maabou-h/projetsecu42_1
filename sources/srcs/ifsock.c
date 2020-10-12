#include "ft_malcolm.h"

char        *network_resolve()
{
    char    *addr;

    if ((addr = get_interface()) == NULL)
    {
        fprintf(stderr, "ft_malcolm: %s\n", "Error finding available network interface");
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
    return (addr);
}