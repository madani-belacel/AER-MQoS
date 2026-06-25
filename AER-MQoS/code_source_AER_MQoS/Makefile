CONTIKI_PROJECT = AER-MQoS-node
all: $(CONTIKI_PROJECT)

CONTIKI ?= ../../../..

# Variante de protocole pour les experiences de l'article :
# RPL_STANDARD | RPL_MQOS | RPL_AER | AER-MQoS
AER_PROTOCOL_VARIANT ?= AER-MQoS

# Avoid mixing newlib (/usr/local/include) with glibc for native Cooja target
unexport CPATH
unexport C_INCLUDE_PATH

# Native Cooja: restrict to GCC + glibc system headers only (no /usr/local/include)
GCC_SYSINC := $(dir $(shell $(CC) -print-libgcc-file-name))include
ifeq ($(TARGET),cooja)
  CFLAGS += -nostdinc
  ifneq ($(GCC_SYSINC),)
    CFLAGS += -isystem $(GCC_SYSINC)
  endif
  GCC_MULTIARCH := $(shell $(CC) -print-multiarch 2>/dev/null)
  ifneq ($(GCC_MULTIARCH),)
    CFLAGS += -isystem /usr/include/$(GCC_MULTIARCH)
  else
    CFLAGS += -isystem /usr/include/x86_64-linux-gnu
  endif
  CFLAGS += -isystem /usr/include
endif

CFLAGS += -include $(CURDIR)/cooja-gcc-compat.h

ifeq ($(AER_PROTOCOL_VARIANT),RPL_STANDARD)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=0
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/variants/imacros-RPL_STANDARD.h
  PROJECT_SOURCEFILES = aer_rpl_plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),RPL_MQOS)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_MQOS=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/variants/imacros-AER-MQoS.h
  PROJECT_SOURCEFILES = aer_rpl_plus.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),RPL_AER)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_AER=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/variants/imacros-AER-MQoS.h
  PROJECT_SOURCEFILES = aer_rpl_plus.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else ifeq ($(AER_PROTOCOL_VARIANT),AER-MQoS)
  CFLAGS += -DAER_RPL_COMPILE_CUSTOM_OF=1 -DAER_MQOS_PROFILE_FULL=1
  CFLAGS += -include $(CURDIR)/AER-MQoS-extern.h
  CFLAGS += -imacros $(CURDIR)/variants/imacros-AER-MQoS.h
  PROJECT_SOURCEFILES = aer_rpl_plus.c rpl-of-aer-plus.c aer_rpl_energy.c aer_rpl_trust.c aer_rpl_qlearn.c aer_qos_queue.c aer_campaign_log.c
else
  $(error Unknown AER_PROTOCOL_VARIANT=$(AER_PROTOCOL_VARIANT). Use RPL_STANDARD, RPL_MQOS, RPL_AER, or AER-MQoS)
endif

# Logs machine-lisibles Cooja : make AER_CONF_CAMPAIGN_METRICS=1 TARGET=cooja
ifdef AER_CONF_CAMPAIGN_METRICS
  CFLAGS += -DAER_CONF_CAMPAIGN_METRICS=$(AER_CONF_CAMPAIGN_METRICS)
endif
ifdef AER_CAMPAIGN_PROTO_TAG
  CFLAGS += -DAER_CAMPAIGN_PROTO_TAG=\"$(AER_CAMPAIGN_PROTO_TAG)\"
endif
ifdef AER_EXTRA_CFLAGS
  CFLAGS += $(AER_EXTRA_CFLAGS)
endif

TARGET ?= cooja

include $(CONTIKI)/Makefile.include
