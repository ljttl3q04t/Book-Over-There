def remove_none_value_in_dict(input_dict):
    return {key: value for key, value in input_dict.items() if value is not None}
