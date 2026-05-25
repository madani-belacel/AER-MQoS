/*
 * Copyright (c) 2026, Madani Belacel.
 * Simulated residual energy (NRE) for Cooja — not a hardware fuel gauge.
 */

#include "aer_rpl_energy.h"
#include "contiki.h"
#include "lib/random.h"
#include "aer_campaign_log.h"

#define N_HISTORY 8

static uint16_t residual_x100 = 7500;
static uint16_t hist[N_HISTORY];
static uint8_t hist_i;

void
aer_rpl_energy_init(void)
{
  uint8_t i;

  for(i = 0; i < N_HISTORY; i++) {
    hist[i] = 7500;
  }
  hist_i = 0;
}

void
aer_rpl_energy_periodic(void)
{
  int16_t drain = 5 + (random_rand() % 12);
  int16_t harvest = 3 + (random_rand() % 25);
  int32_t v;

  v = (int32_t)residual_x100 - drain + harvest;

  if(v < 500) {
    v = 500;
  }
  if(v > 10000) {
    v = 10000;
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
