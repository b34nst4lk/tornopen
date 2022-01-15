def assert_subset_dict(larger_dict, smaller_dict):
    for k, v in smaller_dict.items():
        if isinstance(v, dict):
            assert_subset_dict(larger_dict.get(k), v)
        else:
            assert larger_dict.get(k) == v
