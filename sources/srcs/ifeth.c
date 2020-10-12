#include "ft_malcolm.h"

char                *get_interface()
{
    struct ifaddrs  *ifap;
    struct ifaddrs  *ifa;

    getifaddrs(&ifap);
    for (ifa = ifap; ifa; ifa = ifa->ifa_next)
    {
        if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET && !(ifa->ifa_flags & 0x8))
        {
            printf("Found available interface: %s\n", ifa->ifa_name);
            freeifaddrs(ifap);
            return (ifa->ifa_name);
        }
    }
    freeifaddrs(ifap);
    return (NULL);
}