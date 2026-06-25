/*
 * Workaround pour l'erreur "missing binary operator" dans
 * bits/indirect-return.h sur GCC 13+ / glibc (Cooja natif).
 * On definit _GNU_SOURCE tot pour que pthread_getattr_np() et
 * autres extensions GNU soient visibles avant les includes.
 */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#ifndef COOJA_GCC_COMPAT_H_
#define COOJA_GCC_COMPAT_H_

#ifndef __has_attribute
#define __has_attribute(x) 0
#endif

#ifndef __glibc_has_attribute
#define __glibc_has_attribute(x) __has_attribute(x)
#endif

#ifndef __THROWNL
#define __THROWNL
#endif

#endif
