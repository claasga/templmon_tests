class ConditionFactory:
    def __new__(
        cls,
        required_actions=None,
        prohibitive_actions=None,
        material=None,
        num_personnel=None,
        lab_devices=None,
        area=None,
        role=None,
    ):
        default_conditions = {
            "required_actions": required_actions,
            "prohibitive_actions": prohibitive_actions,
            "material": material,
            "num_personnel": num_personnel,
            "lab_devices": lab_devices,
            "area": area,
            "role": role,
        }
        if required_actions:
            default_conditions["required_actions"] = required_actions
        if prohibitive_actions:
            default_conditions["prohibitive_actions"] = prohibitive_actions
        if material:
            default_conditions["material"] = material
        if num_personnel:
            default_conditions["num_personnel"] = num_personnel
        if lab_devices:
            default_conditions["lab_devices"] = lab_devices
        if area:
            default_conditions["area"] = area
        if role:
            default_conditions["role"] = role
        return default_conditions
