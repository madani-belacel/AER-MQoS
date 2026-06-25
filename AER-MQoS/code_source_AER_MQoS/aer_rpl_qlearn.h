#ifndef AER_RPL_QL_H
#define AER_RPL_QL_H

#include <stdint.h>

void aer_rpl_ql_init(void);

/* Mise a jour periodique du Q-learning (etats de batterie discrets).
   tx_ok = reussites, tx_tot = tentatives dans la fenetre courante */
void aer_rpl_ql_periodic(uint32_t tx_ok, uint32_t tx_tot);

#endif
