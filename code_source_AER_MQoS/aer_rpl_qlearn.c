/*
 * Copyright (c) 2026, Madani Belacel.
 * Bounded Q-table: optional nudge on gamma (see paper appendix).
 */

#include "aer_rpl_qlearn.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include <stdint.h>

#define N_STATES 4
#define N_ACTIONS 3
#define ALPHA_QL 30
#define GAMMA_DISC 90

static int8_t Q[N_STATES][N_ACTIONS];
static uint8_t last_state;
static uint8_t last_action;

static uint8_t
state_from_battery(void)
{
  uint8_t b = aer_energy_get_nre_x100();

  if(b < 25) {
    return 0;
  }
  if(b < 50) {
    return 1;
  }
  if(b < 75) {
    return 2;
  }
  return 3;
}

void
aer_rpl_ql_init(void)
{
  uint8_t s, a;

  for(s = 0; s < N_STATES; s++) {
    for(a = 0; a < N_ACTIONS; a++) {
      Q[s][a] = 0;
    }
  }
  last_state = 0;
  last_action = 1;
}

void
aer_rpl_ql_periodic(uint32_t tx_ok, uint32_t tx_tot)
{
  int32_t reward;
  uint8_t s, s2, a, aa;
  int32_t qsa, max_next, td;

  if(tx_tot == 0) {
    return;
  }

  s = last_state;
  reward = (int32_t)((tx_ok * 100) / tx_tot);
  if(aer_energy_get_nre_x100() < 20) {
    reward -= 15;
  }

  s2 = state_from_battery();
  max_next = Q[s2][0];
  for(a = 1; a < N_ACTIONS; a++) {
    if(Q[s2][a] > max_next) {
      max_next = Q[s2][a];
    }
  }

  qsa = Q[s][last_action];
  td = reward * 2 + (int32_t)((GAMMA_DISC * max_next) / 100) - qsa;
  qsa = qsa + (int32_t)((ALPHA_QL * td) / 100);

  if(qsa > 127) {
    qsa = 127;
  }
  if(qsa < -128) {
    qsa = -128;
  }
  Q[s][last_action] = (int8_t)qsa;

  a = 0;
  for(aa = 1; aa < N_ACTIONS; aa++) {
    if(Q[s2][aa] > Q[s2][a]) {
      a = aa;
    }
  }
  last_state = s2;
  last_action = a;

  if(a == 0) {
    aer_rpl_plus_ql_nudge_gamma(-5);
  } else if(a == 2) {
    aer_rpl_plus_ql_nudge_gamma(5);
  }
}
