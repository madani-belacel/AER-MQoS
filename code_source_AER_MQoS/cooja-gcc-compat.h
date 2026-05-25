/**
 * Évite l'erreur « missing binary operator » dans bits/indirect-return.h
 * sur certaines combinaisons GCC 13+/glibc (Cooja natif).
 */
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
