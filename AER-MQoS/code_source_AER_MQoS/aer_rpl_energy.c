/*
 * Copyright (c) 2026, Madani Belacel.
 *
 * Simulation d'energie residuelle (NRE) sous Cooja.
 * C'est pas une vraie batterie, on simule juste un drain aleatoire
 * avec un peu de harvest pour imiter un panneau solaire (Section V).
 *
 * Fake NRE model + moving-average predictor for Cooja.
 */

#include "aer_rpl_energy.h"
#include "contiki.h"
#include "lib/random.h"
#include "aer_campaign_log.h"

#define N_HISTORY 8
#define ENERGY_INIT_X100 7500
#define ENERGY_MIN_X100 500
#define ENERGY_MAX_X100 10000
#define DRAIN_BASE 5
#define DRAIN_RANGE 12
#define HARVEST_BASE 3
#define HARVEST_RANGE 25

static uint16_t residual_x100 = ENERGY_INIT_X100;
static uint16_t hist[N_HISTORY];
static uint8_t hist_i;

void
aer_rpl_energy_init(void)
{
  uint8_t i;

  for(i = 0; i < N_HISTORY; i++) {
    hist[i] = ENERGY_INIT_X100;
  }
  hist_i = 0;
}

/* Met a jour la batterie simulee et l'historique pour la prediction */
void
aer_rpl_energy_periodic(void)
{
  int16_t drain = DRAIN_BASE + (random_rand() % DRAIN_RANGE);
  int16_t harvest = HARVEST_BASE + (random_rand() % HARVEST_RANGE);
  int32_t v;

  v = (int32_t)residual_x100 - drain + harvest;

  if(v < ENERGY_MIN_X100) {
    v = ENERGY_MIN_X100;
  }
  if(v > ENERGY_MAX_X100) {
    v = ENERGY_MAX_X100;
  }

  residual_x100 = (uint16_t)v;

  hist[hist_i] = residual_x100;
  hist_i = (hist_i + 1) % N_HISTORY;

#if AER_CONF_CAMPAIGN_METRICS
  aer_campaign_log_energy(aer_energy_get_nre_x100(),
       aer_energy_get_pred_x100());
#endif
}

uint8_t
aer_energy_get_nre_x100(void)
{
  return (uint8_t)(residual_x100 / 100);
}

static __attribute__((unused)) uint16_t
aer_energy_get_nre_x100_full(void)
{
  return residual_x100;
}

uint8_t
aer_energy_get_pred_x100(void)
{
  uint32_t s = 0;
  uint8_t i;

  for(i = 0; i < N_HISTORY; i++) {
    s += hist[i];
  }
  return (uint8_t)((s / N_HISTORY) / 100);
}

static __attribute__((unused)) uint16_t
aer_energy_get_pred_x100_full(void)
{
  uint32_t s = 0;
  uint8_t i;

  for(i = 0; i < N_HISTORY; i++) {
    s += hist[i];
  }
  return (uint16_t)(s / N_HISTORY);
}
