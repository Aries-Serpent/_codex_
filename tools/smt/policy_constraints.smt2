(set-logic QF_UF)
(declare-fun online_allowlist () Bool)
(declare-fun host_allowlisted () Bool)
(declare-fun admin_perms () Bool)
(declare-fun action_readonly () Bool)
(declare-fun action_admin () Bool)
(define-fun admissible () Bool
  (and online_allowlist host_allowlisted (or action_readonly (and action_admin admin_perms))))