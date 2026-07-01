#     assert (, "Condition must be true"
#         optimizer._extract_success_signal({"ci_checks_green": True, "ci_checks_red": False}) is None
#     ), "Condition must be true"
#     assert optimizer._extract_success_signal({"ci_checks_green": 3, "ci_checks_red": False}) is None
#     assert optimizer._extract_success_signal({"ci_checks_green": True, "ci_checks_red": 1}) is None
