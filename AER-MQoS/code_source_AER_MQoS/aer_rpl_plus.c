/*
 * Copyright (c) 2026, Madani Belacel, University of Mostaganem.
 *
 * AER-MQoS — noyau de fusion contextuelle (gamma, alpha, beta / MCS).
 * Implémente l'équation du score multicritère (Section III-E du manuscrit).
 *
 * Context fusion core: MCS computation and gamma/alpha/beta update.
 */

#include "contiki.h"
#include "net/link-stats.h"
#include "net/routing/rpl-lite/rpl.h"
#include "net/routing/rpl-lite/rpl-neighbor.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include "aer_rpl_trust.h"

/* Valeur de base du gamma par domaine (0..100). On ajuste ensuite
   suivant la classe de trafic et le niveau de batterie. */
#define GAMMA_HEALTH 80
#define GAMMA_INDUSTRY 70
#define GAMMA_AGRICULTURE 35
#define GAMMA_ENVIRONMENT 25
#define GAMMA_DEFAULT 50

/* Ajustements par classe de trafic */
#define GAMMA_CLASS_C3_ADJ 35
#define GAMMA_CLASS_C2_ADJ 20
#define GAMMA_CLASS_C0_ADJ (-25)

/* Seuils batterie et ajustements correspondants */
#define BATT_LOW_THRESH 20
#define BATT_HIGH_THRESH 80
#define BATT_LOW_ADJ (-20)
#define BATT_HIGH_ADJ 8

/* Poids MCS par classe : w_etx/delay = QoS, w_nre/penergy/trust = energie */
static const uint8_t w_etx[4] = {40, 30, 15, 10};
static const uint8_t w_delay[4] = {10, 20, 35, 40};
static const uint8_t w_nre[4] = {25, 20, 20, 15};
static const uint8_t w_penergy[4] = {20, 20, 20, 20};
#ifndef AER_CONF_W_TRUST
#define AER_CONF_W_TRUST {15, 10, 10, 5}
#endif
static const uint8_t w_trust[4] = AER_CONF_W_TRUST;

static aer_domain_t g_domain = AER_DOMAIN_AGRICULTURE;
static aer_context_weights_t g_weights = {40, 40, 60};
static int8_t ql_gamma_bias;
static aer_traffic_class_t g_app_tc = AER_TRAFFIC_C1_NORMAL;

static uint8_t
clamp_u8(int v)
{
  /* On sature entre 0 et 100 */
  if(v < 0) {
    return 0;
  }
  if(v > 100) {
    return 100;
  }
  return (uint8_t)v;
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

/* Recalcule gamma/alpha/beta : domaine, classe, batterie, biais Q-learning. */
void
aer_rpl_plus_update_context(aer_traffic_class_t traffic, uint8_t battery_x100)
{
  int base_gamma;

  switch(g_domain) {
  case AER_DOMAIN_HEALTH:
    base_gamma = GAMMA_HEALTH;
    break;
  case AER_DOMAIN_INDUSTRY:
    base_gamma = GAMMA_INDUSTRY;
    break;
  case AER_DOMAIN_AGRICULTURE:
    base_gamma = GAMMA_AGRICULTURE;
    break;
  case AER_DOMAIN_ENVIRONMENT:
    base_gamma = GAMMA_ENVIRONMENT;
    break;
  default:
    base_gamma = GAMMA_DEFAULT;
    break;
  }

  switch(traffic) {
  case AER_TRAFFIC_C3_CRITICAL:
    base_gamma += GAMMA_CLASS_C3_ADJ;
    break;
  case AER_TRAFFIC_C2_URGENT:
    base_gamma += GAMMA_CLASS_C2_ADJ;
    break;
  case AER_TRAFFIC_C1_NORMAL:
    break;
  case AER_TRAFFIC_C0_BEST_EFFORT:
    base_gamma += GAMMA_CLASS_C0_ADJ;
    break;
  }

  if(battery_x100 < BATT_LOW_THRESH) {
    base_gamma += BATT_LOW_ADJ;
  } else if(battery_x100 > BATT_HIGH_THRESH) {
    base_gamma += BATT_HIGH_ADJ;
  }

  base_gamma += ql_gamma_bias;

  g_weights.gamma_x100 = clamp_u8(base_gamma);
  g_weights.alpha_x100 = g_weights.gamma_x100;
  g_weights.beta_x100 = g_weights.alpha_x100 > 100 ? 0 : 100 - g_weights.alpha_x100;  /* alpha+beta = 100 */
}

/* Le Q-learning peut deplacer gamma de +-5, on clamp a +-30 pour pas s'emballer */
void
aer_rpl_plus_ql_nudge_gamma(int8_t delta_x100)
{
  int v = (int)ql_gamma_bias + (int)delta_x100;

  if(v > 30) {
    v = 30;
  }
  if(v < -30) {
    v = -30;
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

/* Remplit la structure de metriques pour le logging (utilise par le noeud et le CSV). */
void
aer_rpl_plus_fill_parent_metrics_for_logging(aer_parent_metrics_t *met)
{
  rpl_nbr_t *nb;
  uint16_t etx;
  uint16_t etx_clamped;
  const struct link_stats *stats;

  if(met == NULL) {
    return;
  }
  met->nre_x100 = aer_energy_get_nre_x100();
  met->predicted_energy_x100 = aer_energy_get_pred_x100();

  nb = curr_instance.dag.preferred_parent;
  if(nb == NULL) {
    met->etx_x100 = 0;
    met->delay_ms = AER_DELAY_BASE;
    met->trust_x100 = 50; /* valeur par defaut, neutre */
    return;
  }

  stats = rpl_neighbor_get_link_stats(nb);
  etx = stats != NULL ? stats->etx : 0xffff;
  etx_clamped = etx;
  if(etx_clamped > AER_ETX_CLAMP) {
    etx_clamped = AER_ETX_CLAMP;
  }
  met->etx_x100 = (uint16_t)((etx_clamped * 100UL) / LINK_STATS_ETX_DIVISOR);
  if(met->etx_x100 > AER_ETX_CLAMP) {
    met->etx_x100 = AER_ETX_CLAMP;
  }
  met->delay_ms = (uint16_t)(AER_DELAY_BASE + (uint32_t)etx / 16UL);
  if(met->delay_ms > AER_DELAY_MAX) {
    met->delay_ms = AER_DELAY_MAX;
  }
  met->trust_x100  = aer_trust_for_nbr(nb);
}

static uint16_t
norm_etx(uint16_t etx_x100)
{
  if(etx_x100 > AER_ETX_CLAMP) {
    etx_x100 = AER_ETX_CLAMP;
  }
  return (uint16_t)((etx_x100 * 100UL) / AER_ETX_CLAMP);
}

static uint16_t
norm_delay(uint16_t delay_ms)
{
  if(delay_ms > AER_DELAY_MAX) {
    delay_ms = AER_DELAY_MAX;
  }
  return (uint16_t)((delay_ms * 100UL) / AER_DELAY_MAX);
}

uint16_t
aer_rpl_plus_compute_mcs(const aer_parent_metrics_t *metrics)
{
  uint16_t etx_n, delay_n;

  if(metrics == NULL) {
    return 0;
  }
  uint16_t mcs_qos, mcs_energy;
  uint16_t trust_risk;
  uint8_t tc = g_app_tc;

  if(tc > 3) {
    tc = 0;
  }

  etx_n = norm_etx(metrics->etx_x100);
  delay_n = norm_delay(metrics->delay_ms);

  {
    uint8_t wq = w_etx[tc] + w_delay[tc];
    mcs_qos = (w_etx[tc] * etx_n + w_delay[tc] * delay_n) / wq;
  }

  trust_risk = 100 - metrics->trust_x100;
  {
    uint8_t we = w_nre[tc] + w_penergy[tc] + w_trust[tc];
    mcs_energy = (w_nre[tc] * metrics->nre_x100
        + w_penergy[tc] * metrics->predicted_energy_x100
        + w_trust[tc] * trust_risk) / we;
  }

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
