/*
 * Copyright (c) 2026, Madani Belacel.
 * Experimental RPL objective function (OCP 8) for AER-MQoS.
 */

#include "contiki.h"
#include "rpl-of-aer-plus.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/link-stats.h"
#include "net/routing/rpl-lite/rpl-neighbor.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include "aer_rpl_trust.h"
#include "sys/log.h"

#define LOG_MODULE "RPL"
#define LOG_LEVEL LOG_LEVEL_INFO

#ifdef RPL_MRHOF_CONF_MAX_LINK_METRIC
#define MAX_LINK_METRIC RPL_MRHOF_CONF_MAX_LINK_METRIC
#else
#define MAX_LINK_METRIC 512
#endif

#ifdef RPL_MRHOF_CONF_MAX_PATH_COST
#define MAX_PATH_COST RPL_MRHOF_CONF_MAX_PATH_COST
#else
#define MAX_PATH_COST 32768
#endif

#define RANK_THRESHOLD 192
#define TIME_THRESHOLD (10 * 60 * CLOCK_SECOND)

#ifndef LINK_STATS_ETX_DIVISOR
#define LINK_STATS_ETX_DIVISOR 256
#endif

/*---------------------------------------------------------------------------*/
static void
aer_of_reset(void)
{
  LOG_INFO("reset AER-MQoS OF\n");
}
/*---------------------------------------------------------------------------*/
static uint16_t
aer_of_nbr_link_metric(rpl_nbr_t *nb)
{
  const struct link_stats *stats = rpl_neighbor_get_link_stats(nb);
  return stats != NULL ? stats->etx : 0xffff;
}
/*---------------------------------------------------------------------------*/
static uint16_t
mcs_to_link_rank_addend(rpl_nbr_t *nb)
{
  uint16_t etx;
  uint16_t etx_clamped;
  aer_parent_metrics_t met;
  uint16_t mcs;
  uint32_t addend;

  etx = aer_of_nbr_link_metric(nb);

  aer_rpl_plus_update_context(aer_rpl_plus_get_app_traffic_class(),
      aer_energy_get_nre_x100());

  etx_clamped = etx;
  if(etx_clamped > 800) {
    etx_clamped = 800;
  }
  met.etx_x100 = (uint16_t)((etx_clamped * 100UL) / LINK_STATS_ETX_DIVISOR);
  if(met.etx_x100 > 800) {
    met.etx_x100 = 800;
  }

  met.delay_ms = (uint16_t)(80UL + (uint32_t)etx / 16UL);
  if(met.delay_ms > 1500) {
    met.delay_ms = 1500;
  }

  met.trust_x100 = aer_trust_for_nbr(nb);
  met.nre_x100 = aer_energy_get_nre_x100();
  met.predicted_energy_x100 = aer_energy_get_pred_x100();

  mcs = aer_rpl_plus_compute_mcs(&met);

#if defined(AER_MQOS_PROFILE_MQOS)
  {
    uint16_t delay_boost = MIN(120, met.delay_ms / 6);
    addend = 64UL + (uint32_t)mcs * 4UL + delay_boost;
  }
#elif defined(AER_MQOS_PROFILE_AER)
  addend = 48UL + ((uint32_t)met.etx_x100 * 3UL) / 10UL + (uint32_t)mcs * 3UL;
#else
  addend = 64UL + (uint32_t)mcs * 6UL;
#endif
  if(addend > 700) {
    addend = 700;
  }
  return (uint16_t)addend;
}
/*---------------------------------------------------------------------------*/
static uint16_t
aer_of_nbr_path_cost(rpl_nbr_t *nb)
{
  uint16_t base;

  if(nb == NULL) {
    return 0xffff;
  }

#if RPL_WITH_MC
  switch(curr_instance.mc.type) {
  case RPL_DAG_MC_ETX:
    base = nb->mc.obj.etx;
    break;
  case RPL_DAG_MC_ENERGY:
    base = nb->mc.obj.energy.energy_est << 8;
    break;
  default:
    base = nb->rank;
    break;
  }
#else
  base = nb->rank;
#endif

  return MIN((uint32_t)base + mcs_to_link_rank_addend(nb), 0xffff);
}
/*---------------------------------------------------------------------------*/
static rpl_rank_t
aer_of_rank_via_nbr(rpl_nbr_t *nb)
{
  uint16_t min_hoprankinc;
  uint16_t path_cost;

  if(nb == NULL) {
    return RPL_INFINITE_RANK;
  }

  min_hoprankinc = curr_instance.min_hoprankinc;
  path_cost = aer_of_nbr_path_cost(nb);

  return MAX(MIN((uint32_t)nb->rank + min_hoprankinc, RPL_INFINITE_RANK), path_cost);
}
/*---------------------------------------------------------------------------*/
static int
aer_of_nbr_has_usable_link(rpl_nbr_t *nb)
{
  return aer_of_nbr_link_metric(nb) <= MAX_LINK_METRIC;
}
/*---------------------------------------------------------------------------*/
static int
aer_of_nbr_is_acceptable_parent(rpl_nbr_t *nb)
{
  uint16_t path_cost = aer_of_nbr_path_cost(nb);
  return aer_of_nbr_has_usable_link(nb) && path_cost <= MAX_PATH_COST;
}
/*---------------------------------------------------------------------------*/
static int
aer_of_within_hysteresis(rpl_nbr_t *nb)
{
  uint16_t path_cost = aer_of_nbr_path_cost(nb);
  uint16_t parent_path_cost = aer_of_nbr_path_cost(curr_instance.dag.preferred_parent);
  int within_rank_hysteresis = path_cost + RANK_THRESHOLD > parent_path_cost;
  int within_time_hysteresis = nb->better_parent_since == 0
    || (clock_time() - nb->better_parent_since) <= TIME_THRESHOLD;

  return within_rank_hysteresis && within_time_hysteresis;
}
/*---------------------------------------------------------------------------*/
static rpl_nbr_t *
aer_of_best_parent(rpl_nbr_t *nb1, rpl_nbr_t *nb2)
{
  int ok1 = nb1 != NULL && aer_of_nbr_is_acceptable_parent(nb1);
  int ok2 = nb2 != NULL && aer_of_nbr_is_acceptable_parent(nb2);

  if(!ok1) {
    return ok2 ? nb2 : NULL;
  }
  if(!ok2) {
    return ok1 ? nb1 : NULL;
  }

  if(nb1 == curr_instance.dag.preferred_parent && aer_of_within_hysteresis(nb2)) {
    return nb1;
  }
  if(nb2 == curr_instance.dag.preferred_parent && aer_of_within_hysteresis(nb1)) {
    return nb2;
  }

  return aer_of_nbr_path_cost(nb1) < aer_of_nbr_path_cost(nb2) ? nb1 : nb2;
}
/*---------------------------------------------------------------------------*/
static void
aer_of_update_metric_container(void)
{
  curr_instance.mc.type = RPL_DAG_MC_NONE;
}
/*---------------------------------------------------------------------------*/
rpl_of_t rpl_aer_plus = {
  aer_of_reset,
  aer_of_nbr_link_metric,
  aer_of_nbr_has_usable_link,
  aer_of_nbr_is_acceptable_parent,
  aer_of_nbr_path_cost,
  aer_of_rank_via_nbr,
  aer_of_best_parent,
  aer_of_update_metric_container,
  8
};
