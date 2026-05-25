/**
 * Macros RPL pour -imacros : uniquement des #define.
 * Variantes RPLMQoS-style / AER-RPL-style / AER-MQoS : OCP 8, profil MCS dans rpl-of-aer-plus.c
 * (Makefile : -DAER_MQOS_PROFILE_*). RPL_STANDARD utilise variants/imacros-RPL_STANDARD.h à la place.
 */
#define RPL_CONF_OF_OCP 8
#define RPL_CONF_SUPPORTED_OFS {&rpl_aer_plus}
#define RPL_CONF_MOP RPL_MOP_NON_STORING
#define NETSTACK_CONF_WITH_IPV6 1
#define UIP_CONF_BUFFER_SIZE 1280
#define LOG_CONF_LEVEL_RPL 3
#define LOG_CONF_LEVEL_IPV6 3
#define LOG_CONF_LEVEL_MAC 4
