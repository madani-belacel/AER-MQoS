/*
 * Copyright (c) 2026, Madani Belacel.
 *
 * Petite table Q pour ajuster gamma en ligne. Pas utilise dans
 * les resultats principaux, c'est juste une verification de
 * coherence (sanity check) dans learn_or_load.csv.
 *
 * Bounded Q-learning, optional nudge on gamma (see Appendix).
 */

#include "aer_rpl_qlearn.h"
#include "aer_rpl_plus.h"
#include "aer_rpl_energy.h"
#include "lib/random.h"
#include <stdint.h>

#define N_STATES 4
#define N_ACTIONS 3
#ifndef ALPHA_QL
#define ALPHA_QL 30
#endif
#ifndef GAMMA_DISC
#define GAMMA_DISC 90
#endif
#ifndef EPSILON_QL
#define EPSILON_QL 10
#endif
#define REWARD_LOW_BAT_PENALTY 15
#define GAMMA_NUDGE_DOWN (-5)
#define GAMMA_NUDGE_UP 5

static int8_t Q[N_STATES][N_ACTIONS];
static uint8_t last_state;
static uint8_t last_action;

/* On decoupe la batterie en 4 niveaux (section VI-B) */
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
  reward = (int32_t)(((uint64_t)tx_ok * 100UL) / tx_tot);
  if(aer_energy_get_nre_x100() < 20) {
    reward -= REWARD_LOW_BAT_PENALTY;
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

  if(random_rand() % 100 < EPSILON_QL) {
    a = random_rand() % N_ACTIONS;
  } else {
    a = 0;
    for(aa = 1; aa < N_ACTIONS; aa++) {
      if(Q[s2][aa] > Q[s2][a]) {
        a = aa;
      }
    }
  }
  last_state = s2;
  last_action = a;

  if(a == 0) {
    aer_rpl_plus_ql_nudge_gamma(GAMMA_NUDGE_DOWN);
  } else if(a == 2) {
    aer_rpl_plus_ql_nudge_gamma(GAMMA_NUDGE_UP);
  }
}
