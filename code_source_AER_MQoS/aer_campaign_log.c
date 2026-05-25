/*
 * Copyright (c) 2026, Madani Belacel.
 * METRIC,... CSV lines for parse_cooja_logs.py (disable with AER_CONF_CAMPAIGN_METRICS=0).
 */

#include "contiki.h"
#include "net/linkaddr.h"
#include "sys/node-id.h"
#include "aer_campaign_log.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#if !AER_CONF_CAMPAIGN_METRICS
const int aer_campaign_log_disabled = 0;
#endif

#if AER_CONF_CAMPAIGN_METRICS

static void
parse_kv_udp_sidecar(char *buf, uint32_t *seq_out, unsigned *node_out)
{
  char *tok;

  *seq_out = 0;
  *node_out = 0;
  for(tok = strtok(buf, " "); tok != NULL; tok = strtok(NULL, " ")) {
    unsigned long vseq = 0;
    unsigned vnode = 0;

    if(sscanf(tok, "t=%lu", &vseq) == 1) {
      *seq_out = (uint32_t)vseq;
    }
    if(sscanf(tok, "n=%u", &vnode) == 1) {
      *node_out = vnode;
    }
  }
}

static uint32_t
time_ms(void)
{
  return (uint32_t)((1000UL * (unsigned long)clock_time()) /
                    (unsigned long)CLOCK_SECOND);
}

void
aer_campaign_log_tx(uint32_t app_seq, uint8_t traffic_class, uint16_t payload_len)
{
  printf("METRIC,TX,%lu,%02x%02x,%lu,%u,%u,%u,%s\n",
         (unsigned long)time_ms(),
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 2],
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 1],
         (unsigned long)app_seq,
         (unsigned)traffic_class,
         (unsigned)payload_len,
         (unsigned)node_id,
         AER_CAMPAIGN_PROTO_TAG);
}

void
aer_campaign_log_rx(const uint8_t *payload, uint16_t payload_len)
{
  uint32_t app_seq = 0;
  unsigned sender_node = 0;

  if(payload != NULL && payload_len > 0) {
    char tmp[128];
    size_t n = payload_len < sizeof(tmp) - 1 ? payload_len : sizeof(tmp) - 1;

    memcpy(tmp, payload, n);
    tmp[n] = '\0';
    parse_kv_udp_sidecar(tmp, &app_seq, &sender_node);
  }

  printf("METRIC,RX,%lu,%02x%02x,%lu,%u,%u,%s\n",
         (unsigned long)time_ms(),
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 2],
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 1],
         (unsigned long)app_seq,
         (unsigned)payload_len,
         (unsigned)sender_node,
         AER_CAMPAIGN_PROTO_TAG);
}

void
aer_campaign_log_energy(uint8_t nre_x100, uint8_t pred_x100)
{
  printf("METRIC,NRJ,%lu,%02x%02x,%u,%u,%s\n",
         (unsigned long)time_ms(),
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 2],
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 1],
         (unsigned)nre_x100,
         (unsigned)pred_x100,
         AER_CAMPAIGN_PROTO_TAG);
}

void
aer_campaign_log_ctx(uint8_t class_id, uint8_t alpha_x100, uint8_t beta_x100, uint8_t gamma_x100)
{
  printf("METRIC,CTX,%lu,%02x%02x,%u,%u,%u,%u,%s\n",
         (unsigned long)time_ms(),
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 2],
         (unsigned)linkaddr_node_addr.u8[LINKADDR_SIZE - 1],
         (unsigned)class_id,
         (unsigned)alpha_x100,
         (unsigned)beta_x100,
         (unsigned)gamma_x100,
         AER_CAMPAIGN_PROTO_TAG);
}

#endif /* AER_CONF_CAMPAIGN_METRICS */
