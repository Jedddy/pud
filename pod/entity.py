class GoBack:
    name = "Back"

    def __repr__(self) -> str:
        return "<<< Go Back"


class Entity:
    """Represents an entity to display on the screen.

    Attributes
    ----------
    name:
        The name of the entity.

    is_file:
        Indicates if this entity is a file or not.
    """

    def __init__(self, name: str, is_file: bool):
        self._name = name
        self._is_file = is_file

        if self._is_file:
            self.emoji = "📄"
        else:
            self.emoji = "📁"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_file(self) -> bool:
        return self._is_file

    def __repr__(self) -> str:
        return f"{self.emoji} {self.name}"
