/*
 * Copyright (c) 2026, Madani Belacel.
 * Cooja campaign node: UDP traffic, WRR queues, METRIC logging.
 */

#include "contiki.h"
#include "net/routing/routing.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip-ds6.h"
#include "net/netstack.h"
#include "sys/log.h"
#include "sys/node-id.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include "aer_rpl_qlearn.h"
#include "aer_qos_queue.h"
#include "aer_campaign_log.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define LOG_MODULE "AER-APP"
#define LOG_LEVEL LOG_LEVEL_INFO

#define UDP_PORT 8765
#define SEND_INTERVAL_BASE   (30 * CLOCK_SECOND)
#define QOS_DRAIN_INTERVAL   (CLOCK_SECOND / 10)

static struct simple_udp_connection udp_conn;
static uint32_t tx_counter;
static uint32_t ql_tx_ok_win;
static uint32_t ql_tx_tot_win;

PROCESS(aer_rpl_plus_node_process, "AER-MQoS node process");
AUTOSTART_PROCESSES(&aer_rpl_plus_node_process);

/* node_id % 4: staggered periods and class bias (heterogeneous C0..C3 load) */
static unsigned
traffic_profile(void)
{
  return (unsigned)node_id % 4u;
}

static clock_time_t
app_send_period(void)
{
  static const clock_time_t mult_num[4] = { 14, 11, 9, 7 };
  static const clock_time_t mult_den[4] = { 10, 10, 10, 10 };
  unsigned p = traffic_profile();

  return (SEND_INTERVAL_BASE * mult_num[p]) / mult_den[p];
}

static aer_traffic_class_t
pick_traffic_class(void)
{
  unsigned pr = traffic_profile();
  uint32_t n = tx_counter;

  if((n % 20u) < 12u) {
    switch(pr) {
    case 0:
      return AER_TRAFFIC_C0_BEST_EFFORT;
    case 1:
      return AER_TRAFFIC_C1_NORMAL;
    case 2:
      return AER_TRAFFIC_C2_URGENT;
    default:
      return AER_TRAFFIC_C3_CRITICAL;
    }
  }
  switch(n % 4u) {
  case 0:
    return AER_TRAFFIC_C3_CRITICAL;
  case 1:
    return AER_TRAFFIC_C2_URGENT;
  case 2:
    return AER_TRAFFIC_C1_NORMAL;
  default:
    return AER_TRAFFIC_C0_BEST_EFFORT;
  }
}

static void
udp_rx_cb(struct simple_udp_connection *c,
          const uip_ipaddr_t *sender_addr,
          uint16_t sender_port,
          const uip_ipaddr_t *receiver_addr,
          uint16_t receiver_port,
          const uint8_t *data,
          uint16_t datalen)
{
  LOG_INFO("rx %u bytes from ", datalen);
  LOG_INFO_6ADDR(sender_addr);
  LOG_INFO_("\n");
  aer_campaign_log_rx(data, datalen);
}

PROCESS_THREAD(aer_rpl_plus_node_process, ev, data)
{
  static struct etimer periodic;
  static struct etimer qos_drain;
  static aer_parent_metrics_t pm;
  static char payload[112];

  PROCESS_BEGIN();

  simple_udp_register(&udp_conn, UDP_PORT, NULL, UDP_PORT, udp_rx_cb);

  if(node_id == 1) {
    NETSTACK_ROUTING.root_start();
  }

  aer_qos_init();
  aer_rpl_plus_init(AER_DOMAIN_AGRICULTURE);
  aer_rpl_energy_init();
  aer_rpl_ql_init();
  ql_tx_ok_win = 0;
  ql_tx_tot_win = 0;

  if(NETSTACK_ROUTING.node_is_root()) {
#if AER_RPL_COMPILE_CUSTOM_OF
    LOG_INFO("Role=root, custom OF OCP=8 (%s)\n", AER_CAMPAIGN_PROTO_TAG);
#else
    LOG_INFO("Role=root, RPL MRHOF (baseline)\n");
#endif
  } else {
    LOG_INFO("Role=node\n");
  }

  etimer_set(&periodic, app_send_period());
  etimer_set(&qos_drain, QOS_DRAIN_INTERVAL);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&periodic) ||
                              etimer_expired(&qos_drain));

    if(etimer_expired(&qos_drain)) {
      struct aer_qos_packet *qp;
      int drain_budget;

      for(drain_budget = 0; drain_budget < 8; drain_budget++) {
        qp = aer_qos_dequeue();
        if(qp == NULL) {
          break;
        }
        aer_rpl_plus_set_app_traffic_class((aer_traffic_class_t)qp->traffic_class);
        aer_rpl_plus_update_context((aer_traffic_class_t)qp->traffic_class,
                                    aer_energy_get_nre_x100());
        simple_udp_sendto(qp->conn, qp->data, qp->len, &qp->dest);
        ql_tx_tot_win++;
        ql_tx_ok_win++;
        aer_campaign_log_tx(tx_counter, (uint8_t)qp->traffic_class, qp->len);
        LOG_INFO("sent (qos): class=%u len=%u\n",
                 (unsigned)qp->traffic_class, (unsigned)qp->len);
        aer_qos_packet_release(qp);
      }
      etimer_reset(&qos_drain);
    }

    if(!etimer_expired(&periodic)) {
      continue;
    }

    tx_counter++;
    aer_rpl_energy_periodic();

    if(!NETSTACK_ROUTING.node_is_root() && NETSTACK_ROUTING.node_is_reachable()) {
      aer_traffic_class_t tc;
      uint8_t batt;

      tc = pick_traffic_class();
      aer_rpl_plus_set_app_traffic_class(tc);
      batt = aer_energy_get_nre_x100();
      aer_rpl_plus_update_context(tc, batt);

      aer_rpl_plus_fill_parent_metrics_for_logging(&pm);

      {
        uint16_t mcs = aer_rpl_plus_compute_mcs(&pm);
        uint8_t path_level = aer_rpl_plus_choose_path_level(tc);
        aer_context_weights_t w = aer_rpl_plus_get_weights();

#if AER_CONF_CAMPAIGN_METRICS
        aer_campaign_log_ctx((uint8_t)tc, w.alpha_x100, w.beta_x100, w.gamma_x100);
#endif
        snprintf(payload, sizeof(payload),
                 "t=%lu c=%s p=%u m=%u g=%u n=%u",
                 (unsigned long)tx_counter,
                 aer_traffic_to_str(tc),
                 (unsigned)path_level,
                 (unsigned)mcs,
                 (unsigned)w.gamma_x100,
                 (unsigned)node_id);
      }

      {
        uip_ipaddr_t dest_ipaddr;

        if(NETSTACK_ROUTING.get_root_ipaddr(&dest_ipaddr)) {
          aer_qos_set_pending_dest(&dest_ipaddr);
          if(aer_qos_enqueue(&udp_conn,
                             (const uint8_t *)payload,
                             (uint16_t)strlen(payload),
                             (uint8_t)tc) != 0) {
            simple_udp_sendto(&udp_conn, payload, strlen(payload), &dest_ipaddr);
            ql_tx_tot_win++;
            ql_tx_ok_win++;
            aer_campaign_log_tx(tx_counter, (uint8_t)tc, (uint16_t)strlen(payload));
            LOG_INFO("sent direct: %s\n", payload);
          } else {
            LOG_INFO("queued: %s\n", payload);
          }
        } else {
          ql_tx_tot_win++;
          LOG_INFO("root addr unavailable\n");
        }
      }
    } else {
      if(NETSTACK_ROUTING.node_is_root()) {
        LOG_INFO("root alive, tx_counter=%lu\n", (unsigned long)tx_counter);
      } else {
        LOG_INFO("not reachable yet\n");
      }
    }

    if(!NETSTACK_ROUTING.node_is_root()) {
      if(ql_tx_tot_win > 0) {
        aer_rpl_ql_periodic(ql_tx_ok_win, ql_tx_tot_win);
      }
      ql_tx_ok_win = 0;
      ql_tx_tot_win = 0;
    } else {
      ql_tx_ok_win = 0;
      ql_tx_tot_win = 0;
    }

    etimer_reset(&periodic);
  }

  PROCESS_END();
}
