from constants import models


class Constants:
    """
    Generic Constants class.

    This class holds all constants registered.
    """

    def __init__(self):
        """Initialize."""
        self.constants = {}

    @staticmethod
    def _change_nullable(constant: models.Constant, nullable: bool, default_value):
        """Change nullable value of constant."""
        if constant.nullable != nullable:
            if constant.nullable and not nullable:
                if constant.get_value() is None:
                    constant.set_value(default_value)
            constant.nullable = nullable

    @staticmethod
    def _create_constant(slug, constant_type, nullable, default_value):
        """Create a new constant"""
        constant = models.Constant.objects.create(slug=slug, type=constant_type, nullable=nullable, value="")
        try:
            constant.set_value(default_value)
        except TypeError as e:
            constant.delete()
            raise e
        constant.save()
        return constant

    def register_constant(self, slug: str, constant_type: int, nullable: bool, default_value=None):
        """Add a constant to the constants."""
        if not nullable and default_value is None:
            raise Exception("{} is not nullable but does not have a default value.".format(slug))

        if self.is_registered(slug):
            raise Exception("{} is already registered".format(slug))

        if models.Constant.objects.filter(slug=slug).exists():
            # Constant already exists
            constant = models.Constant.objects.get(slug=slug)
            if constant.type != constant_type:
                constant.delete()
                constant = self._create_constant(slug, constant_type, nullable, default_value)
            else:
                self._change_nullable(constant, nullable, default_value)
                constant.save()
            self.constants[slug] = constant
        else:
            # Constant is new
            constant = self._create_constant(slug, constant_type, nullable, default_value)
            self.constants[slug] = constant

    def is_registered(self, slug: str) -> bool:
        """Check if a constant is registered"""
        return slug in self.constants.keys()

    def get_constant(self, slug: str) -> models.Constant:
        """Get a constant."""
        if not self.is_registered(slug):
            raise ValueError("Constant {} not in registered constants".format(slug))

        try:
            return models.Constant.objects.get(slug=slug)
        except models.Constant.DoesNotExist:
            raise Exception("Constant {} is not registered in the database".format(slug))

    def get_value(self, constant: str):
        """Get the value of a constant."""
        constant = self.get_constant(constant)
        return constant.get_value()

    def set_value(self, constant: str, value):
        """Set the value of a constant."""
        constant = self.get_constant(constant)
        constant.set_value(value)
        constant.save()


constants = Constants()
