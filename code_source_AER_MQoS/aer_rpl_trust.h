#ifndef AER_RPL_TRUST_H
#define AER_RPL_TRUST_H

#include "net/routing/rpl-lite/rpl.h"

/**
 * Trust score 0..100 derived from link statistics (ETX) toward the neighbor.
 * Stronger reputation or attack-detection hooks can extend this mapping later.
 */
uint8_t aer_trust_for_nbr(rpl_nbr_t *neighbor);

#endif
