/*
 * Lignes de log lisibles par machine pour les campagnes Cooja.
 * Chaque ligne commence par "METRIC,". Activer avec
 * -DAER_CONF_CAMPAIGN_METRICS=1.  Les stubs vides evite de
 * polluer le firmware en release.
 *
 * Machine-readable METRIC lines for Cooja campaigns.
 */
#ifndef AER_CAMPAIGN_LOG_H_
#define AER_CAMPAIGN_LOG_H_
#include <stdint.h>

#ifndef AER_CONF_CAMPAIGN_METRICS
#define AER_CONF_CAMPAIGN_METRICS 0
#endif
#ifndef AER_CAMPAIGN_PROTO_TAG
#define AER_CAMPAIGN_PROTO_TAG "AER-MQoS"
#endif

#if AER_CONF_CAMPAIGN_METRICS
void aer_campaign_log_tx(uint32_t app_seq, uint8_t traffic_class, uint16_t payload_len);
void aer_campaign_log_rx(const uint8_t *payload, uint16_t payload_len);
void aer_campaign_log_energy(uint8_t nre_x100, uint8_t pred_x100);
void aer_campaign_log_ctx(uint8_t class_id, uint8_t alpha_x100, uint8_t beta_x100, uint8_t gamma_x100);
#else
#define aer_campaign_log_tx(app_seq, traffic_class, payload_len) ((void)0)
#define aer_campaign_log_rx(payload, payload_len) ((void)0)
#define aer_campaign_log_energy(nre_x100, pred_x100) ((void)0)
#define aer_campaign_log_ctx(class_id, alpha_x100, beta_x100, gamma_x100) ((void)0)
#endif
#endif /* AER_CAMPAIGN_LOG_H_ */
