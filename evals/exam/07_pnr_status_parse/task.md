parse_status breaks on real IRCTC texts like 'CNF/S4/33/UB' (berth type at the end), 'RAC/23', 'GNWL/24', 'PQWL 5',
and on lowercase text users type like 'wl 12'. All waiting-list quotas (GNWL, PQWL, RLWL, ...) should come back as
status 'WL'. Make it handle these.
