#ifndef AER_RPL_PLUS_H_
#define AER_RPL_PLUS_H_
/*
 * Copyright (c) 2026, Madani Belacel.
 *
 * Header public du module AER-MQoS : classes de trafic,
 * poids contextuels (gamma/alpha/beta), score MCS, etc.
 */

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Shared constants for MCS normalisation (ETX clamp & delay range). */
#ifndef AER_ETX_CLAMP
#define AER_ETX_CLAMP 800
#endif
#ifndef AER_DELAY_BASE
#define AER_DELAY_BASE 80
#endif
#ifndef AER_DELAY_MAX
#define AER_DELAY_MAX 1500
#endif

typedef enum {
  AER_DOMAIN_HEALTH = 0,
  AER_DOMAIN_AGRICULTURE,
  AER_DOMAIN_INDUSTRY,
  AER_DOMAIN_ENVIRONMENT
} aer_domain_t;

typedef enum {
  AER_TRAFFIC_C0_BEST_EFFORT = 0,
  AER_TRAFFIC_C1_NORMAL,
  AER_TRAFFIC_C2_URGENT,
  AER_TRAFFIC_C3_CRITICAL
} aer_traffic_class_t;

typedef struct {
  uint16_t etx_x100;
  uint16_t delay_ms;
  uint8_t trust_x100;
  uint8_t nre_x100;
  uint8_t predicted_energy_x100;
} aer_parent_metrics_t;

typedef struct {
  uint8_t gamma_x100;
  uint8_t alpha_x100;
  uint8_t beta_x100;
} aer_context_weights_t;

void aer_rpl_plus_init(aer_domain_t dom);
void aer_rpl_plus_set_domain(aer_domain_t dom);
aer_domain_t aer_rpl_plus_get_domain(void);

void aer_rpl_plus_set_app_traffic_class(aer_traffic_class_t tc);
aer_traffic_class_t aer_rpl_plus_get_app_traffic_class(void);

void aer_rpl_plus_update_context(aer_traffic_class_t traffic, uint8_t battery_x100);
aer_context_weights_t aer_rpl_plus_get_weights(void);

void aer_rpl_plus_ql_nudge_gamma(int8_t delta_x100);

uint16_t aer_rpl_plus_compute_mcs(const aer_parent_metrics_t *metrics);
uint8_t aer_rpl_plus_choose_path_level(aer_traffic_class_t traffic);

void aer_rpl_plus_fill_parent_metrics_for_logging(aer_parent_metrics_t *met);

const char *aer_traffic_to_str(aer_traffic_class_t c);

#ifdef __cplusplus
}
#endif

#endif /* AER_RPL_PLUS_H_ */
