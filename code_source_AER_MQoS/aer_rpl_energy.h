#ifndef AER_RPL_ENERGY_H
#define AER_RPL_ENERGY_H

#include <stdint.h>

void aer_rpl_energy_init(void);
void aer_rpl_energy_periodic(void);

uint8_t aer_energy_get_nre_x100(void);
uint8_t aer_energy_get_pred_x100(void);

#endif
