/*
 * Copyright (c) 2026, Madani Belacel.
 * Four UDP queues (C0..C3) with weighted round-robin (4:3:2:1).
 */

#include "contiki.h"
#include "lib/memb.h"
#include "lib/list.h"
#include "aer_qos_queue.h"
#include "sys/log.h"
#include <string.h>

#define LOG_MODULE "AER-QoS"
#define LOG_LEVEL LOG_LEVEL_INFO

LIST(aer_qos_q0);
LIST(aer_qos_q1);
LIST(aer_qos_q2);
LIST(aer_qos_q3);

MEMB(aer_qos_memb, struct aer_qos_packet, AER_QOS_MEMB_BLOCKS);

/* WRR cycle: C3×4, C2×3, C1×2, C0×1 */
static const uint8_t wrr_cycle[AER_QOS_WRR_CYCLE_LEN] =
  { 3, 3, 3, 3, 2, 2, 2, 1, 1, 0 };

static uint8_t wrr_pos;
static uint8_t last_served_class;
static uip_ipaddr_t pending_dest;
static uint8_t pending_dest_set;

/*---------------------------------------------------------------------------*/
static list_t
queue_for_class(uint8_t cl)
{
  switch(cl) {
  case 0:
    return aer_qos_q0;
  case 1:
    return aer_qos_q1;
  case 2:
    return aer_qos_q2;
  case 3:
    return aer_qos_q3;
  default:
    LOG_WARN("invalid class %u, using C3\n", (unsigned)cl);
    return aer_qos_q3;
  }
}
/*---------------------------------------------------------------------------*/
void
aer_qos_init(void)
{
  memb_init(&aer_qos_memb);
  list_init(aer_qos_q0);
  list_init(aer_qos_q1);
  list_init(aer_qos_q2);
  list_init(aer_qos_q3);

  wrr_pos = 0;
  last_served_class = 0;
  pending_dest_set = 0;
  memset(&pending_dest, 0, sizeof(pending_dest));
}
/*---------------------------------------------------------------------------*/
void
aer_qos_set_pending_dest(const uip_ipaddr_t *dest)
{
  if(dest == NULL) {
    pending_dest_set = 0;
    return;
  }
  uip_ipaddr_copy(&pending_dest, dest);
  pending_dest_set = 1;
}
/*---------------------------------------------------------------------------*/
int
aer_qos_enqueue(struct simple_udp_connection *c,
                const uint8_t *data,
                uint16_t len,
                uint8_t traffic_class)
{
  struct aer_qos_packet *p;
  list_t q;

  if(c == NULL || data == NULL) {
    return -1;
  }
  if(!pending_dest_set) {
    return -1;
  }
  if(traffic_class > 3) {
    return -1;
  }
  if(len == 0 || len > AER_QOS_MAX_PAYLOAD) {
    return -1;
  }

  q = queue_for_class(traffic_class);
  if(list_length(q) >= AER_QOS_QUEUE_MAX_PER_CLASS) {
    return -1;
  }

  p = memb_alloc(&aer_qos_memb);
  if(p == NULL) {
    return -1;
  }

  p->conn = c;
  uip_ipaddr_copy(&p->dest, &pending_dest);
  p->len = len;
  p->traffic_class = traffic_class;
  memcpy(p->data, data, len);

  list_add(q, p);
  return 0;
}
/*---------------------------------------------------------------------------*/
struct aer_qos_packet *
aer_qos_dequeue(void)
{
  int n;

  for(n = 0; n < AER_QOS_WRR_CYCLE_LEN; n++) {
    uint8_t cl = wrr_cycle[wrr_pos];
    list_t q = queue_for_class(cl);

    if(list_head(q) != NULL) {
      struct aer_qos_packet *p = (struct aer_qos_packet *)list_pop(q);

      wrr_pos = (uint8_t)((wrr_pos + 1) % AER_QOS_WRR_CYCLE_LEN);
      last_served_class = cl;
      return p;
    }

    wrr_pos = (uint8_t)((wrr_pos + 1) % AER_QOS_WRR_CYCLE_LEN);
  }

  return NULL;
}
/*---------------------------------------------------------------------------*/
void
aer_qos_packet_release(struct aer_qos_packet *p)
{
  if(p == NULL) {
    return;
  }
  memb_free(&aer_qos_memb, p);
}
/*---------------------------------------------------------------------------*/
uint8_t
aer_qos_get_current_class(void)
{
  return last_served_class;
}
/*---------------------------------------------------------------------------*/
