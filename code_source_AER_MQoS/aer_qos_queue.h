/**
 * \file
 *         Files d'attente QoS par classe (C0–C3) + ordonnancement WRR léger.
 * \brief
 *         Couche applicative : tampons bornés + poids 4:3:2:1 (C3…C0).
 *
 *         L’adresse de destination UDP n’est pas dans la signature historique
 *         à quatre paramètres : appeler aer_qos_set_pending_dest() avant
 *         chaque aer_qos_enqueue() (ou une fois si la destination ne change pas).
 */
#ifndef AER_QOS_QUEUE_H_
#define AER_QOS_QUEUE_H_

#include "contiki.h"
#include "net/ipv6/uip.h"
#include <stdint.h>

struct simple_udp_connection;

#ifndef AER_QOS_MAX_PAYLOAD
/** Taille max copiée par paquet (réduire sur Sky / Z1 si besoin). */
#define AER_QOS_MAX_PAYLOAD 72
#endif

#ifndef AER_QOS_QUEUE_MAX_PER_CLASS
/** Profondeur max par file (classe). */
#define AER_QOS_QUEUE_MAX_PER_CLASS 8
#endif

#ifndef AER_QOS_MEMB_BLOCKS
/**
 * Nombre total de blocs memb (plafond global mémoire).
 * Doit être >= 1 ; typiquement <= 4 * AER_QOS_QUEUE_MAX_PER_CLASS.
 */
#define AER_QOS_MEMB_BLOCKS 12
#endif

#ifndef AER_QOS_WRR_CYCLE_LEN
/** Longueur du motif WRR (4+3+2+1 services par tour complet). */
#define AER_QOS_WRR_CYCLE_LEN 10
#endif

/**
 * Descripteur de paquet en file (équivalent logique du « struct packet » du
 * cahier des charges : une fois dequeue, envoyer puis aer_qos_packet_release()).
 *
 * Le premier champ doit être un pointeur (API list.h de Contiki-NG).
 */
struct aer_qos_packet {
  struct aer_qos_packet *next;
  struct simple_udp_connection *conn;
  uip_ipaddr_t dest;
  uint16_t len;
  uint8_t traffic_class;
  uint8_t data[AER_QOS_MAX_PAYLOAD];
};

void aer_qos_init(void);

/**
 * Fixe la prochaine adresse IPv6 utilisée par aer_qos_enqueue().
 * Obligatoire avant le premier enqueue vers une nouvelle destination.
 */
void aer_qos_set_pending_dest(const uip_ipaddr_t *dest);

/**
 * Enfile une copie des données pour la classe traffic_class (0=C0 … 3=C3).
 * \retval 0  OK
 * \retval -1 file classe pleine, pool mémoire plein, destination non définie,
 *             ou len trop grande
 */
int aer_qos_enqueue(struct simple_udp_connection *c,
                    const uint8_t *data,
                    uint16_t len,
                    uint8_t traffic_class);

/**
 * Retire un paquet selon WRR (poids C3:C2:C1:C0 = 4:3:2:1).
 * \return NULL si toutes les files sont vides
 */
struct aer_qos_packet *aer_qos_dequeue(void);

/** Libère un descripteur retourné par aer_qos_dequeue() (obligatoire). */
void aer_qos_packet_release(struct aer_qos_packet *p);

/** Dernière classe servie par aer_qos_dequeue() (0–3), ou 0 si jamais servi. */
uint8_t aer_qos_get_current_class(void);

#endif /* AER_QOS_QUEUE_H_ */
