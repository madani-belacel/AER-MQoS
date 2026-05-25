/**
 * Inclus tout en premier (-include) pour que rpl-dag / rpl-conf voient le symbole OF.
 */
#ifndef AER_MQOS_EXTERN_H_
#define AER_MQOS_EXTERN_H_

struct rpl_of;
#if AER_RPL_COMPILE_CUSTOM_OF
extern struct rpl_of rpl_aer_plus;
#else
extern struct rpl_of rpl_mrhof;
#endif

#endif
