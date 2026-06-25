#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/* Configuration supplementaire (LOG, etc.). Les macros RPL critiques
   sont dans variants/imacros-*.h (CFLAGS -imacros) et le symbole OF
   dans AER-MQoS-extern.h (-include). */

/* Application log level: 0=off, 1=err, 2=warn, 3=info, 4=debug */
#define LOG_CONF_LEVEL_APP LOG_LEVEL_DBG
#ifndef LOG_CONF_LEVEL_RPL
#define LOG_CONF_LEVEL_RPL LOG_LEVEL_WARN
#endif
#ifndef LOG_CONF_LEVEL_MAC
#define LOG_CONF_LEVEL_MAC LOG_LEVEL_WARN
#endif
#define QUEUEBUF_CONF_NUM 16

#endif /* PROJECT_CONF_H_ */
