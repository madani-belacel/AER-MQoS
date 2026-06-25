#ifndef AER_RPL_TRUST_H
#define AER_RPL_TRUST_H

#include "net/routing/rpl-lite/rpl.h"

/* Score de confiance 0..100 a partir de l'ETX du voisin.
   On pourra ajouter des hooks de reputation ou detection d'attaque
   plus tard si besoin. */
uint8_t aer_trust_for_nbr(rpl_nbr_t *neighbor);

#endif
