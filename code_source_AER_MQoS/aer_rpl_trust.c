/*
 * Copyright (c) 2026, Madani Belacel.
 * Link-reliability score (LRS) from neighbor ETX for the MCS.
 */

#include "contiki.h"
#include "aer_rpl_trust.h"
#include "net/link-stats.h"
#include "net/routing/rpl-lite/rpl-neighbor.h"

#ifndef LINK_STATS_ETX_DIVISOR
#define LINK_STATS_ETX_DIVISOR 256
#endif

#define TRUST_DEFAULT_NO_NBR  40
#define TRUST_DEFAULT_BAD_ETX 45

uint8_t
aer_trust_for_nbr(rpl_nbr_t *neighbor)
{
  const struct link_stats *stats;
  uint32_t etx;
  uint32_t t;

  if(neighbor == NULL) {
    return TRUST_DEFAULT_NO_NBR;
  }

  stats = rpl_neighbor_get_link_stats(neighbor);
  if(stats == NULL || stats->etx >= 0xfe00) {
    return TRUST_DEFAULT_BAD_ETX;
  }

  etx = stats->etx;
  t = (100UL * LINK_STATS_ETX_DIVISOR) / (1 + (etx / 4));
  if(t > 100) {
    t = 100;
  }
  return (uint8_t)t;
}
