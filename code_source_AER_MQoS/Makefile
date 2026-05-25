CONTIKI_PROJECT = AER-MQoS-node
all: $(CONTIKI_PROJECT)

CONTIKI ?= ../../../..

# Protocol build tag for article experiments: RPL_STANDARD | RPL_MQOS | RPL_AER | AER_MQOS
AER_PROTOCOL_VARIANT ?= AER_MQOS

# Avoid mixing newlib (/usr/local/include) with glibc for native Cooja target
unexport CPATH
unexport C_INCLUDE_PATH

# Native Cooja: restrict to GCC + glibc system headers only (no /usr/local/include)
GCC_SYSINC := /usr/lib/gcc/x86_64-linux-gnu/$(shell $(CC) -dumpversion)/include
ifeq ($(TARGET),cooja)
  CFLAGS += -nostdinc
  CFLAGS += -isystem $(GCC_SYSINC)
  CFLAGS += -isystem /usr/include/x86_64-linux-gnu
  CFLAGS += -isystem /usr/include
endif

CFLAGS += -include $(CURDIR)/cooja-gcc-compat.h

ifeq ($(AER_PROTOCOL_VARIANT),RPL_STANDARD)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=0
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/variants/imacros-RPL_STANDARD.h
  PROJECT_SOURCEFILES = aer_mqos.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),RPL_MQOS)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_MQOS=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/AER-MQoS-macros.h
  PROJECT_SOURCEFILES = aer_mqos.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),RPL_AER)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_AER=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/AER-MQoS-macros.h
  PROJECT_SOURCEFILES = aer_mqos.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),AER_MQOS)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_FULL=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/AER-MQoS-macros.h
  PROJECT_SOURCEFILES = aer_mqos.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else
  $(error Unknown AER_PROTOCOL_VARIANT=$(AER_PROTOCOL_VARIANT). Use RPL_STANDARD, RPL_MQOS, RPL_AER, or AER_MQOS)
endif

# Logs machine-lisibles Cooja : make AER_CONF_CAMPAIGN_METRICS=1 TARGET=cooja
ifdef AER_CONF_CAMPAIGN_METRICS
  CFLAGS += -DAER_CONF_CAMPAIGN_METRICS=$(AER_CONF_CAMPAIGN_METRICS)
endif
ifdef AER_CAMPAIGN_PROTO_TAG
  CFLAGS += -DAER_CAMPAIGN_PROTO_TAG=\"$(AER_CAMPAIGN_PROTO_TAG)\"
endif

TARGET ?= cooja

include $(CONTIKI)/Makefile.include
