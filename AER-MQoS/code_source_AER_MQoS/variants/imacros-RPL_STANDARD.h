/* Variante RPL standard : MRHOF (OCP 1), pas d'extensions AER-MQoS.
   Sert de ligne de base dans les campagnes de simulation. */

#define RPL_CONF_OF_OCP 1
#define RPL_CONF_SUPPORTED_OFS {&rpl_mrhof}
#define RPL_CONF_MOP RPL_MOP_NON_STORING
#define NETSTACK_CONF_WITH_IPV6 1
#define UIP_CONF_BUFFER_SIZE 1280
#define LOG_CONF_LEVEL_RPL 3
#define LOG_CONF_LEVEL_IPV6 3
#define LOG_CONF_LEVEL_MAC 4
