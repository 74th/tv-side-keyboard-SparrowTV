from typing import Any, TypeAlias, Union

LEDColor: TypeAlias = "tuple[int, int, int]"  # g, r, b

ActionCode = int
Action: TypeAlias = "Union[ActionCode, tuple[ActionCode, Any]]"
KeyAssign: TypeAlias = "Union[Action, list[Action], None]"
Layer: TypeAlias = "list[list[KeyAssign]]"
Layers: TypeAlias = "list[Layer]"
LayerLED: TypeAlias = "list[list[Union[LEDColor, None]]]"
LayersLED: TypeAlias = "list[LayerLED]"
