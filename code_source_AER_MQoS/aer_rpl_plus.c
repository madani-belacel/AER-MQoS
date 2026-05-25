/*
 * Copyright (c) 2026, Madani Belacel, University of Mostaganem.
 * AER-MQoS — MCS and context fusion (gamma, alpha, beta).
 */

#include "contiki.h"
#include "net/link-stats.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-neighbor.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include "aer_rpl_trust.h"

/* MCS partial weights (0..100 scale) */
#define W1_ETX           25
#define W2_DELAY         25
#define W3_NRE           20
#define W4_PRED_ENERGY   20
#define W5_TRUST_RISK    10

static aer_domain_t g_domain = AER_DOMAIN_AGRICULTURE;
static aer_context_weights_t g_weights = {40, 40, 60};
static int8_t ql_gamma_bias;
static aer_traffic_class_t g_app_tc = AER_TRAFFIC_C1_NORMAL;

static uint8_t
clamp_u8(int v)
{
  if(v < 0) {
    return 0;
  }
  if(v > 100) {
    return 100;
  }
  return (uint8_t)v;
}

const char *
aer_domain_to_str(aer_domain_t d)
{
  switch(d) {
  case AER_DOMAIN_HEALTH:
    return "health";
  case AER_DOMAIN_AGRICULTURE:
    return "agriculture";
  case AER_DOMAIN_INDUSTRY:
    return "industry";
  case AER_DOMAIN_ENVIRONMENT:
    return "environment";
  default:
    return "unknown";
  }
}

const char *
aer_traffic_to_str(aer_traffic_class_t c)
{
  switch(c) {
  case AER_TRAFFIC_C0_BEST_EFFORT:
    return "C0";
  case AER_TRAFFIC_C1_NORMAL:
    return "C1";
  case AER_TRAFFIC_C2_URGENT:
    return "C2";
  case AER_TRAFFIC_C3_CRITICAL:
    return "C3";
  default:
    return "C?";
  }
}

void
aer_rpl_plus_init(aer_domain_t dom)
{
  aer_rpl_plus_set_domain(dom);
}

void
aer_rpl_plus_set_domain(aer_domain_t dom)
{
  g_domain = dom;
}

void
aer_rpl_plus_set_app_traffic_class(aer_traffic_class_t tc)
{
  g_app_tc = tc;
}

aer_traffic_class_t
aer_rpl_plus_get_app_traffic_class(void)
{
  return g_app_tc;
}

aer_domain_t
aer_rpl_plus_get_domain(void)
{
  return g_domain;
}

void
aer_rpl_plus_update_context(aer_traffic_class_t traffic, uint8_t battery_x100)
{
  int base_gamma;

  switch(g_domain) {
  case AER_DOMAIN_HEALTH:
    base_gamma = 80;
    break;
  case AER_DOMAIN_INDUSTRY:
    base_gamma = 70;
    break;
  case AER_DOMAIN_AGRICULTURE:
    base_gamma = 35;
    break;
  case AER_DOMAIN_ENVIRONMENT:
    base_gamma = 25;
    break;
  default:
    base_gamma = 50;
    break;
  }

  switch(traffic) {
  case AER_TRAFFIC_C3_CRITICAL:
    base_gamma += 15;
    break;
  case AER_TRAFFIC_C2_URGENT:
    base_gamma += 10;
    break;
  case AER_TRAFFIC_C1_NORMAL:
    break;
  case AER_TRAFFIC_C0_BEST_EFFORT:
    base_gamma -= 10;
    break;
  }

  if(battery_x100 < 20) {
    base_gamma -= 12;
  } else if(battery_x100 > 80) {
    base_gamma += 4;
  }

  base_gamma += ql_gamma_bias;

  g_weights.gamma_x100 = clamp_u8(base_gamma);
  g_weights.alpha_x100 = g_weights.gamma_x100;
  g_weights.beta_x100 = 100 - g_weights.alpha_x100;
}

void
aer_rpl_plus_ql_nudge_gamma(int8_t delta_x100)
{
  int v = (int)ql_gamma_bias + (int)delta_x100;

  if(v > 15) {
    v = 15;
  }
  if(v < -15) {
    v = -15;
  }
  ql_gamma_bias = (int8_t)v;
}

aer_context_weights_t
aer_rpl_plus_get_weights(void)
{
  return g_weights;
}

#ifndef LINK_STATS_ETX_DIVISOR
#define LINK_STATS_ETX_DIVISOR 256
#endif

void
aer_rpl_plus_fill_parent_metrics_for_logging(aer_parent_metrics_t *met)
{
  rpl_nbr_t *nb;
  uint16_t etx;
  uint16_t etx_clamped;
  const struct link_stats *stats;

  met->nre_x100 = aer_energy_get_nre_x100();
  met->predicted_energy_x100 = aer_energy_get_pred_x100();

  nb = curr_instance.dag.preferred_parent;
  if(nb == NULL) {
    met->etx_x100 = 0;
    met->delay_ms = 80;
    met->trust_x100 = 50;
    return;
  }

  stats = rpl_neighbor_get_link_stats(nb);
  etx = stats != NULL ? stats->etx : 0xffff;
  etx_clamped = etx;
  if(etx_clamped > 800) {
    etx_clamped = 800;
  }
  met->etx_x100 = (uint16_t)((etx_clamped * 100UL) / LINK_STATS_ETX_DIVISOR);
  if(met.etx_x100 > 800) {
    met->etx_x100 = 800;
  }
  met->delay_ms = (uint16_t)(80UL + (uint32_t)etx / 16UL);
  if(met->delay_ms > 1500) {
    met->delay_ms = 1500;
  }
  met->trust_x100 = aer_trust_for_nbr(nb);
}

static uint16_t
norm_etx(uint16_t etx_x100)
{
  if(etx_x100 > 800) {
    etx_x100 = 800;
  }
  return (uint16_t)((etx_x100 * 100UL) / 800UL);
}

static uint16_t
norm_delay(uint16_t delay_ms)
{
  if(delay_ms > 1500) {
    delay_ms = 1500;
  }
  return (uint16_t)((delay_ms * 100UL) / 1500UL);
}

uint16_t
aer_rpl_plus_compute_mcs(const aer_parent_metrics_t *metrics)
{
  uint16_t etx_n, delay_n;
  uint16_t mcs_qos, mcs_energy;
  uint16_t trust_risk;

  etx_n = norm_etx(metrics->etx_x100);
  delay_n = norm_delay(metrics->delay_ms);

  mcs_qos = (W1_ETX * etx_n + W2_DELAY * delay_n) / (W1_ETX + W2_DELAY);

  trust_risk = 100 - metrics->trust_x100;
  mcs_energy = (W3_NRE * metrics->nre_x100
      + W4_PRED_ENERGY * metrics->predicted_energy_x100
      + W5_TRUST_RISK * trust_risk)
      / (W3_NRE + W4_PRED_ENERGY + W5_TRUST_RISK);

  return (uint16_t)((g_weights.alpha_x100 * mcs_qos
        + g_weights.beta_x100 * mcs_energy) / 100U);
}

uint8_t
aer_rpl_plus_choose_path_level(aer_traffic_class_t traffic)
{
  switch(traffic) {
  case AER_TRAFFIC_C3_CRITICAL:
    return 1;
  case AER_TRAFFIC_C2_URGENT:
    return 2;
  case AER_TRAFFIC_C1_NORMAL:
    return 3;
  case AER_TRAFFIC_C0_BEST_EFFORT:
  default:
    return 4;
  }
}
