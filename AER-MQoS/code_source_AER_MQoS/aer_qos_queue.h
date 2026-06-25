/*
 * Files QoS par classe (C0..C3) + petit ordonnanceur WRR.
 * Poids 6:3:2:1 (C3..C0), buffers bornes.
 * Attention : l'adresse UDP destination se configure via
 * aer_qos_set_pending_dest() avant chaque enqueue().
 *
 * QoS queues per class + lightweight WRR scheduler.
 */
#ifndef AER_QOS_QUEUE_H_
#define AER_QOS_QUEUE_H_

#include "contiki.h"
#include "net/ipv6/uip.h"
#include <stdint.h>

struct simple_udp_connection;

#ifndef AER_QOS_MAX_PAYLOAD
/* Taille max du payload copie par paquet (a reduire sur Sky/Z1) */
#define AER_QOS_MAX_PAYLOAD 72
#endif

#ifndef AER_QOS_QUEUE_MAX_PER_CLASS
/* Profondeur max par file */
#define AER_QOS_QUEUE_MAX_PER_CLASS 16
#endif

#ifndef AER_QOS_MEMB_BLOCKS
/* Nombre total de blocs memb (plafond memoire global).
   En general <= 4 * AER_QOS_QUEUE_MAX_PER_CLASS */
#define AER_QOS_MEMB_BLOCKS 64
#endif

#ifndef AER_QOS_WRR_CYCLE_LEN
/* Longueur du cycle WRR (6+3+2+1 services par tour complet) */
#define AER_QOS_WRR_CYCLE_LEN 12
#endif

/*
 * Descripteur d'un paquet en file. Apres dequeue, on envoie puis
 * on appelle aer_qos_packet_release(). Le premier champ doit etre
 * un pointeur (API list.h de Contiki-NG).
 */
struct aer_qos_packet {
  struct aer_qos_packet *next;
  struct simple_udp_connection *conn;
  uip_ipaddr_t dest;
  uint16_t len;
  uint32_t seq;
  uint8_t traffic_class;
  uint8_t data[AER_QOS_MAX_PAYLOAD];
};

void aer_qos_init(void);

/* Configure l'adresse IPv6 pour le prochain aer_qos_enqueue() */
void aer_qos_set_pending_dest(const uip_ipaddr_t *dest);

/* Met en file un paquet pour la classe traffic_class (0=C0 ... 3=C3).
   Retourne 0 si OK, -1 si probleme (file pleine, memoire, etc.). */
int aer_qos_enqueue(struct simple_udp_connection *c,
                    const uint8_t *data,
                    uint16_t len,
                    uint8_t traffic_class,
                    uint32_t seq);

/* Extrait un paquet selon le WRR (poids 6:3:2:1). Retourne NULL si vide. */
struct aer_qos_packet *aer_qos_dequeue(void);

/* Nombre total de paquets dans toutes les files (C0+C1+C2+C3) */
uint8_t aer_qos_total_occupancy(void);

/* Libere un descripteur recupere par aer_qos_dequeue() */
void aer_qos_packet_release(struct aer_qos_packet *p);

#endif /* AER_QOS_QUEUE_H_ */
