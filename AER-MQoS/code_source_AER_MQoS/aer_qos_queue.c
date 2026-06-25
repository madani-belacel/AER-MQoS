/*
 * Copyright (c) 2026, Madani Belacel.
 *
 * Quatre files UDP (C0..C3) avec round-robin pondere 6:3:2:1 pour
 * l'ordonnancement applicative (Sections III-G et V-D).
 *
 * Application-layer QoS: four UDP queues + WRR scheduler.
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

/* Cycle WRR : C3 six fois, C2 trois fois, C1 deux fois, C0 une fois */
static const uint8_t wrr_cycle[AER_QOS_WRR_CYCLE_LEN] =
  { 3, 3, 3, 3, 3, 3, 2, 2, 2, 1, 1, 0 };

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
    LOG_ERR("invalid class %u, using C3\n", (unsigned)cl);
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
                uint8_t traffic_class,
                uint32_t seq)
{
  struct aer_qos_packet *p;
  list_t q;
  int need_drop;

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

  /* On regarde d'abord si la file est pleine, sans allouer */
  need_drop = (list_length(q) >= AER_QOS_QUEUE_MAX_PER_CLASS);

  if(need_drop) {
    uint8_t drop_cl;
    int dropped = 0;

    /* Head-drop : on vire d'abord le plus vieux paquet de plus basse priorite */
    for(drop_cl = 0; drop_cl < traffic_class; drop_cl++) {
      list_t dq = queue_for_class(drop_cl);
      struct aer_qos_packet *victim = (struct aer_qos_packet *)list_pop(dq);
      if(victim != NULL) {
        memb_free(&aer_qos_memb, victim);
        dropped = 1;
        break;
      }
    }

    /* Si aucune classe inferieure n'avait de paquet, on drop depuis sa propre file */
    if(!dropped && list_length(q) > 0) {
      struct aer_qos_packet *victim = (struct aer_qos_packet *)list_pop(q);
      if(victim != NULL) {
        memb_free(&aer_qos_memb, victim);
        dropped = 1;
      }
    }

    if(!dropped) {
      return -1;
    }
  }

  p = memb_alloc(&aer_qos_memb);
  if(p == NULL) {
    /* Si le pool est vide, on libere un vieux paquet (pareil que le head-drop) */
    uint8_t drop_cl;
    int dropped = 0;

    for(drop_cl = 0; drop_cl <= 3; drop_cl++) {
      list_t dq = queue_for_class(drop_cl);
      struct aer_qos_packet *victim = (struct aer_qos_packet *)list_pop(dq);
      if(victim != NULL) {
        memb_free(&aer_qos_memb, victim);
        dropped = 1;
        break;
      }
    }

    if(!dropped) {
      return -1;
    }

    p = memb_alloc(&aer_qos_memb);
    if(p == NULL) {
      return -1;
    }
  }

  p->conn = c;
  uip_ipaddr_copy(&p->dest, &pending_dest);
  p->len = len;
  p->seq = seq;
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

    /* File vide : on avance le cycle sans consommer le slot.
       Le slot sera retente au prochain appel. */
    wrr_pos = (uint8_t)((wrr_pos + 1) % AER_QOS_WRR_CYCLE_LEN);
  }

  return NULL;
}
/*---------------------------------------------------------------------------*/
uint8_t
aer_qos_total_occupancy(void)
{
  uint8_t n = 0;
  n += (uint8_t)list_length(aer_qos_q0);
  n += (uint8_t)list_length(aer_qos_q1);
  n += (uint8_t)list_length(aer_qos_q2);
  n += (uint8_t)list_length(aer_qos_q3);
  return n;
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
