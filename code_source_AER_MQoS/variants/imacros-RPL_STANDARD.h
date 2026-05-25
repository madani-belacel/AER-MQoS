/**
 * RPL_STANDARD variant: MRHOF (OCP 1), same MOP and IPv6 stack as other campaign builds.
 * Used with AER_PROTOCOL_VARIANT=RPL_STANDARD (without rpl-of-aer-plus.c).
 * AER_RPL_COMPILE_CUSTOM_OF is set from the project Makefile (0 for this variant).
 */#define RPL_CONF_OF_OCP 1
#define RPL_CONF_SUPPORTED_OFS {&rpl_mrhof}
#define RPL_CONF_MOP RPL_MOP_NON_STORING
#define NETSTACK_CONF_WITH_IPV6 1
#define UIP_CONF_BUFFER_SIZE 1280
#define LOG_CONF_LEVEL_RPL 3
#define LOG_CONF_LEVEL_IPV6 3
#define LOG_CONF_LEVEL_MAC 4
