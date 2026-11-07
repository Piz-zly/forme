"""Aides communes aux tests de bout en bout (tests/t*.py).

    from commun import check, fails, termine, clean

check(libellé, ok, détail) affiche OK ou FAIL (avec le détail en cas d'échec) ; termine() affiche le
résumé et termine avec le code 1 si un contrôle a échoué (0 sinon).
"""
import re, sys

fails = []

def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if not ok and extra != '' else ''))
    if not ok: fails.append(label)

# espaces insécables (fine U+202F et normale U+00A0) écrites par toLocaleString('fr-FR') -> espace simple
clean = lambda t: re.sub('[  ]', ' ', t)

def termine():
    print('\n' + ('TOUT EST OK' if not fails else '%d ECHEC(S) : %s' % (len(fails), fails)))
    sys.exit(1 if fails else 0)
