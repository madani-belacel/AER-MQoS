#ifndef AER_RPL_QL_H
#define AER_RPL_QL_H

#include <stdint.h>

void aer_rpl_ql_init(void);

/**
 * Mise à jour périodique Q-learning léger (états discrets batterie).
 * \param tx_ok transmissions réussies sur la fenêtre
 * \param tx_tot transmissions tentées
 */
void aer_rpl_ql_periodic(uint32_t tx_ok, uint32_t tx_tot);

#endif
