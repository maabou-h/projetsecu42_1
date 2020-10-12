#include "ft_malcolm.h"

void                parseipaddr(struct in_addr* in_addr, char* str)
{
  struct hostent    *hostp;

    in_addr->s_addr = inet_addr(str);
    if ((int)in_addr->s_addr == -1)
    {
        if(!(hostp = gethostbyname(str)))
        {
            fprintf(stderr, "ft_malcolm: unknown host or invalid IP address: (%s).\n", str);
            exit(1);
        }
        ft_memcpy(hostp->h_addr, in_addr, hostp->h_length);
    }
}

void                parsemacaddr(char* buf, char* str)
{
    int     i;
    char    c;
    char    val;
    char    *tmp;

    tmp = str;
    for (i=0 ; i < ETHMACADDRLEN ; i++)
    {
        if(!(c = ft_tolower(*str++)))
        {
            fprintf(stderr, "%s: (%s)\n", "ft_malcolm: invalid mac address", tmp);
            exit(1);
        }
        if(ft_isdigit(c))
            val = c - '0';
        else if (c >= 'a' && c <= 'f')
            val = c - 'a' + 10;
        else
        {
            fprintf(stderr, "%s: (%s)\n", "ft_malcolm: invalid mac address", tmp);
            exit(1);
        }
        *buf = val << 4;
        if(!(c = ft_tolower(*str++)))
        {
            fprintf(stderr, "%s: (%s)\n", "ft_malcolm: invalid mac address", tmp);
            exit(1);
        }
        if(ft_isdigit(c))
            val = c - '0';
        else if (c >= 'a' && c <= 'f')
            val = c - 'a' + 10;
        else
        {
            fprintf(stderr, "%s: (%s)\n", "ft_malcolm: invalid mac address", tmp);
            exit(1);
        }
        *buf++ |= val;
        if (*str == ':')
            str++;
    }
}