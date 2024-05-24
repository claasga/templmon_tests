from django.db import models

from game.assignable import Assignable
from game.channel_notifications import MaterialInstanceDispatcher
from helpers.one_or_more_field_not_null import one_or_more_field_not_null


class MaterialInstance(models.Model, Assignable):
    class Meta:
        constraints = [
            one_or_more_field_not_null(["patient_instance", "area", "lab"], "material")
        ]

    action_instance = models.ForeignKey(
        "game.ActionInstance", on_delete=models.SET_NULL, null=True, blank=True
    )
    area = models.ForeignKey("Area", on_delete=models.CASCADE, null=True, blank=True)
    lab = models.ForeignKey("Lab", on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey("template.Material", on_delete=models.CASCADE)
    patient_instance = models.ForeignKey(
        "PatientInstance", on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def name(self):
        return self.template.name

    def save(self, *args, **kwargs):
        changes = kwargs.get("update_fields", None)
        MaterialInstanceDispatcher.save_and_notify(
            self, changes, super(), *args, **kwargs
        )

    def delete(self, using=None, keep_parents=False):
        MaterialInstanceDispatcher.delete_and_notify(self)

    @property
    def is_reusable(self):
        return self.template.is_reusable

    @classmethod
    def generate_materials(cls, materials_recipe, area):
        for template, amount in materials_recipe.items():
            for _ in range(amount):
                cls.objects.create(template=template, area=area)

    def consume(self):
        self.delete()

    def __str__(self):
        return f"{self.name} ({self.id}) assigned to {self.attached_instance()}"
