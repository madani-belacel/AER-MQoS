/* Variante AER-MQoS complete : OF custom (OCP 8), WRR, fusion contextuelle, Q-learning */
#define RPL_CONF_OF_OCP 8
#define RPL_CONF_SUPPORTED_OFS {&rpl_aer_plus}
#define RPL_CONF_MOP RPL_MOP_NON_STORING
#define NETSTACK_CONF_WITH_IPV6 1
#define UIP_CONF_BUFFER_SIZE 1280
#define LOG_CONF_LEVEL_RPL 2
#define LOG_CONF_LEVEL_IPV6 2
#define LOG_CONF_LEVEL_MAC 2
