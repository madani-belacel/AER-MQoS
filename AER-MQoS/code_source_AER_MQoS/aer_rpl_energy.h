#ifndef AER_RPL_ENERGY_H
#define AER_RPL_ENERGY_H

#include <stdint.h>

/* Initialisation et mise a jour periodique du modele d'energie */
void aer_rpl_energy_init(void);
void aer_rpl_energy_periodic(void);

/* Lecture du niveau courant (NRE) et de la prediction moving-average */
uint8_t aer_energy_get_nre_x100(void);
uint8_t aer_energy_get_pred_x100(void);

#endif
