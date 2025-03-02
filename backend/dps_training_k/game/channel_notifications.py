import logging
import asyncio
import os

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import game.models as models  # needed to avoid circular imports
import template.models as template

from collections import defaultdict
from .redis_comm import publish_to_process

"""
This package is responsible to decide when to notify which consumers.
This also implies that it should be as transparent as possible to the models it watches.
Events must be sent as strings, thus objects are passed by ids.
Sending events is done by the celery worker.
"""
PROCESS_ID = int(os.environ.get("PROCESS_ID"))
PARTNER_PROCESS_ID = int(os.environ.get("PARTNER_PROCESS_ID"))


class ChannelEventTypes:
    STATE_CHANGE_EVENT = "state.change.event"
    EXERCISE_UPDATE = "send.exercise.event"
    EXERCISE_START_EVENT = "exercise.start.event"
    EXERCISE_END_EVENT = "exercise.end.event"
    ACTION_CONFIRMATION_EVENT = "action.confirmation.event"
    ACTION_LIST_EVENT = "action.list.event"
    ACTION_CHECK_CHANGED_EVENT = "action.check.changed.event"
    LOG_UPDATE_EVENT = "log.update.event"
    RESOURCE_ASSIGNMENT_EVENT = "resource.assignment.event"
    RELOCATION_START_EVENT = "relocation.start.event"
    RELOCATION_END_EVENT = "relocation.end.event"
    SINGULAR_VIOLATION_EVENT = "singular.violation.event"
    DURATIONAL_VIOLATION_START_EVENT = "durational.violation.start.event"
    DURATIONAL_VIOLATION_END_EVENT = "durational.violation.end.event"
    DURATIONAL_VIOLATION_UPDATE_EVENT = "durational.violation.update.event"
    VIOLATION_PROCESSING_FINISHED = "violation.processing.finished.event"

    # PERSONNEL_ASSIGNED_EVENT = "personnel.assigned.event"
    # PERSONNEL_UNASSIGNED_EVENT = "personnel.unassigned.event"
    TRIAGE_UPDATE_EVENT = "triage.update.event"


def _notify_group(group_channel_name, event):
    """
    Handled internally by the channels' dispatcher. Will try to call a method with event.type as name at the receiver; "." are replaced by "_".
    For more info look into:
    https://channels.readthedocs.io/en/stable/topics/channel_layers.html?highlight=periods#what-to-send-over-the-channel-layer
    """
    async_to_sync(get_channel_layer().group_send)(group_channel_name, event)


async def _async_notify_group(group_channel_name, event):
    await get_channel_layer().group_send(group_channel_name, event)


class ChannelNotifier:
    @classmethod
    # If used in overwritten save method, it must be called before any calls to super().save
    def save_and_notify(cls, obj, changes, save_origin, *args, **kwargs):
        is_updated = not obj._state.adding
        if is_updated and not changes:
            message = f"""{obj.__class__.__name__} have to be saved with save(update_fields=[...]) after initial creation.
           This is to ensure that the frontend is notified of changes."""
            logging.warning(message)

        save_origin.save(*args, **kwargs)
        cls.dispatch_event(obj, changes, is_updated)
        cls.create_trainer_log(obj, changes, is_updated)
        cls._notify_action_check_update(cls.get_exercise(obj))

    @classmethod
    def delete_and_notify(cls, obj, changes):
        raise NotImplementedError(
            "Method delete_and_notify must be implemented by subclass"
        )

    @classmethod
    def get_exercise(cls, obj):
        raise NotImplementedError("Method get_exercise must be implemented by subclass")

    @classmethod
    def get_group_name(cls, obj):
        return f"{obj.__class__.__name__}_{obj.id}"

    @classmethod
    def get_live_group_name(cls, exercise):
        return f"{cls.__name__}_{exercise.id}_live"

    @classmethod
    def dispatch_event(cls, obj, changes):
        raise NotImplementedError(
            "Method dispatch_event must be implemented by subclass"
        )

    @classmethod
    def create_trainer_log(cls, obj, changes, is_updated):
        pass

    @classmethod
    def _notify_exercise_update(cls, exercise):
        channel = cls.get_group_name(exercise)
        event = {
            "type": ChannelEventTypes.EXERCISE_UPDATE,
            "exercise_pk": exercise.id,
        }
        _notify_group(channel, event)

    @classmethod
    def _notify_action_check_update(cls, exercise):
        channel = cls.get_live_group_name(exercise)
        event = {"type": ChannelEventTypes.ACTION_CHECK_CHANGED_EVENT}
        _notify_group(channel, event)

    @classmethod
    def type_to_notifier(cls):
        return {
            models.PatientInstance: PatientInstanceDispatcher,
            models.Area: AreaDispatcher,
            models.Lab: LabDispatcher,
            models.MaterialInstance: MaterialInstanceDispatcher,
            models.Personnel: PersonnelDispatcher,
        }

    @classmethod
    def get_exercise_from_instance(cls, instance):
        notifier_class = cls.type_to_notifier().get(type(instance))
        if notifier_class:
            return notifier_class.get_exercise(instance)
        raise NotImplementedError(
            f"No exercise getter implemented for type {type(instance).__name__}"
        )


class ActionInstanceDispatcher(ChannelNotifier):
    @classmethod
    def dispatch_event(cls, applied_action, changes, is_updated):
        if not changes or ["historic_patient_state"] == changes:
            return

        channel = cls.get_group_name(
            applied_action.patient_instance
            if applied_action.patient_instance
            else applied_action.lab
        )

        if "current_state" in changes:
            if applied_action.state_name == models.ActionInstanceStateNames.PLANNED:
                cls._notify_action_event(
                    ChannelEventTypes.ACTION_CONFIRMATION_EVENT,
                    channel,
                    applied_action,
                )
            if applied_action.template.relocates:
                if (
                    applied_action.state_name
                    == models.ActionInstanceStateNames.IN_PROGRESS
                ):
                    cls._notify_action_event(
                        ChannelEventTypes.RELOCATION_START_EVENT,
                        channel,
                        applied_action,
                    )
                elif (
                    applied_action.state_name
                    == models.ActionInstanceStateNames.FINISHED
                ):
                    cls._notify_action_event(
                        ChannelEventTypes.RELOCATION_END_EVENT,
                        channel,
                        applied_action,
                    )
                    cls._notify_exercise_update(cls.get_exercise(applied_action))

        # always send action list event
        cls._notify_action_event(ChannelEventTypes.ACTION_LIST_EVENT, channel)

    @classmethod
    def _notify_action_event(cls, event_type, channel, applied_action=None):
        # ACTION_LIST_EVENT is a special case, as it does not need an associated applied_Action
        if (
            not event_type == ChannelEventTypes.ACTION_LIST_EVENT
            and not applied_action.patient_instance
            and not applied_action.lab
        ):
            raise ValueError(
                "ActionInstance must be associated with a patient_instance or lab."
            )

        event = {
            "type": event_type,
            "action_instance_id": applied_action.id if applied_action else None,
        }
        _notify_group(channel, event)

    @classmethod
    def create_trainer_log(cls, applied_action, changes, is_updated):
        if changes and "historic_patient_state" in changes:
            return
        if applied_action == models.ActionInstanceStateNames.PLANNED:
            return

        category = models.LogEntry.CATEGORIES.ACTION
        type = None
        content = {}
        content["name"] = applied_action.name
        send_personnel_and_material = False
        if applied_action.state_name == models.ActionInstanceStateNames.IN_PROGRESS:
            type = models.LogEntry.TYPES.STARTED
            send_personnel_and_material = True
        elif applied_action.state_name == models.ActionInstanceStateNames.FINISHED:
            type = models.LogEntry.TYPES.FINISHED
            if applied_action.template.category == template.Action.Category.PRODUCTION:
                named_produced_resources = {
                    material.name: amount
                    for material, amount in applied_action.template.produced_resources().items()
                }
                content["produced"] = str(named_produced_resources)
            if applied_action.template.category == template.Action.Category.EXAMINATION:
                content["examination_result"] = applied_action.result
        elif (
            applied_action.state_name == models.ActionInstanceStateNames.CANCELED
            and applied_action.states.filter(
                name=models.ActionInstanceStateNames.IN_PROGRESS
            ).exists()
        ):
            type = models.LogEntry.TYPES.CANCELED
        elif applied_action.state_name == models.ActionInstanceStateNames.IN_EFFECT:
            type = models.LogEntry.TYPES.IN_EFFECT
        elif applied_action.state_name == models.ActionInstanceStateNames.EXPIRED:
            type = models.LogEntry.TYPES.EXPIRED
        if send_personnel_and_material:
            log_entry = models.LogEntry.objects.create(
                exercise=applied_action.exercise,
                category=category,
                type=type,
                content=content,
                patient_instance=applied_action.patient_instance,
                area=applied_action.destination_area,
                is_dirty=True,
            )
            personnel_list = models.Personnel.objects.filter(
                action_instance=applied_action
            )
            log_entry.personnel.add(*personnel_list)
            material_list = models.MaterialInstance.objects.filter(
                action_instance=applied_action
            )
            log_entry.materials.add(*material_list)
            log_entry.is_dirty = False
            log_entry.save()
        else:
            log_entry = models.LogEntry.objects.create(
                exercise=applied_action.exercise,
                category=category,
                type=type,
                content=content,
                patient_instance=applied_action.patient_instance,
                area=applied_action.destination_area,
            )

    @classmethod
    def delete_and_notify(cls, action_instance, *args, **kwargs):
        attached_instance = action_instance.attached_instance()
        super(action_instance.__class__, action_instance).delete(*args, **kwargs)
        cls._notify_action_event(
            ChannelEventTypes.ACTION_LIST_EVENT, cls.get_group_name(attached_instance)
        )

    @classmethod
    def get_exercise(cls, applied_action):
        return applied_action.exercise


class AreaDispatcher(ChannelNotifier):
    @classmethod
    def dispatch_event(cls, area, changes, is_updated):
        cls._notify_exercise_update(cls.get_exercise(area))

    @classmethod
    def delete_and_notify(cls, area, *args, **kwargs):
        exercise = cls.get_exercise(area)
        super(area.__class__, area).delete(*args, **kwargs)
        cls._notify_exercise_update(exercise)

    @classmethod
    def get_exercise(cls, area):
        return area.exercise


class ExerciseDispatcher(ChannelNotifier):
    @classmethod
    def dispatch_event(cls, obj, changes, is_updated):
        if changes and "state" in changes:
            if obj.state == models.Exercise.StateTypes.RUNNING:
                cls._notify_exercise_start_event(obj)
            if obj.state == models.Exercise.StateTypes.FINISHED:
                cls._notify_exercise_end_event(obj)

    @classmethod
    def create_trainer_log(cls, exercise, changes, is_updated):
        if not is_updated:
            return
        if (
            changes
            and "state" in changes
            and exercise.state == models.Exercise.StateTypes.RUNNING
        ):
            models.LogEntry.objects.create(
                exercise=exercise,
                category=models.LogEntry.CATEGORIES.EXERCISE,
                type=models.LogEntry.TYPES.STARTED,
            )

    @classmethod
    def get_exercise(cls, exercise):
        return exercise

    @classmethod
    def _notify_exercise_start_event(cls, exercise):
        channel = cls.get_group_name(exercise)
        event = {"type": ChannelEventTypes.EXERCISE_START_EVENT}
        _notify_group(channel, event)

        event = {"type": ChannelEventTypes.RESOURCE_ASSIGNMENT_EVENT}
        _notify_group(channel, event)

    @classmethod
    def _notify_exercise_end_event(cls, exercise):
        channel = cls.get_group_name(exercise)
        event = {"type": ChannelEventTypes.EXERCISE_END_EVENT}
        _notify_group(channel, event)


def redis_publish_obj(data):
    exercise_frontend_id = data.get("exercise_frontend_id")
    obj = models.LogEntry.objects.get(id=data.get("obj_id"))
    LogEntryDispatcher._publish_obj(obj, exercise_frontend_id)


class Observable:
    _exercise_subscribers = defaultdict(set)

    @classmethod
    def subscribe_to_exercise(
        cls, exercise_frontend_id, subscriber, send_past_logs=False
    ):
        cls._exercise_subscribers[exercise_frontend_id].add(subscriber)
        if send_past_logs:
            past_logs = models.LogEntry.objects.filter(
                exercise__frontend_id=exercise_frontend_id
            ).order_by("timestamp", "pk")
            for log_entry in past_logs:
                subscriber.receive_log_entry(log_entry)

    @classmethod
    def unsubscribe_from_exercise(cls, exercise_frontend_id, subscriber):
        if exercise_frontend_id in cls._exercise_subscribers:
            cls._exercise_subscribers[exercise_frontend_id].remove(subscriber)

    @classmethod
    def _publish_obj(cls, obj, exercise_frontend_id):
        if not obj.is_valid():
            return

        if PROCESS_ID == 1:
            publish_to_process(
                PARTNER_PROCESS_ID,
                {"obj_id": obj.id, "exercise_frontend_id": exercise_frontend_id},
            )
            return
        if exercise_frontend_id in cls._exercise_subscribers:
            for subscriber in cls._exercise_subscribers[exercise_frontend_id]:
                subscriber.receive_log_entry(obj)


class LogEntryDispatcher(Observable, ChannelNotifier):

    @classmethod
    def save_and_notify(cls, obj, changes, save_origin, *args, **kwargs):
        super().save_and_notify(obj, changes, save_origin, *args, **kwargs)
        cls._publish_obj(obj, obj.exercise.frontend_id)

    @classmethod
    def get_group_name(cls, exercise):
        return f"{exercise.__class__.__name__}_{exercise.id}_log"

    @classmethod
    def get_exercise(cls, log_entry):
        return log_entry.exercise

    @classmethod
    def dispatch_event(cls, log_entry, changes, is_updated):
        if log_entry.is_valid():
            cls._notify_log_update_event(log_entry)

    @classmethod
    def _notify_log_update_event(cls, log_entry):
        channel = cls.get_group_name(log_entry.exercise)
        event = {
            "type": ChannelEventTypes.LOG_UPDATE_EVENT,
            "log_entry_id": log_entry.id,
        }
        _notify_group(channel, event)


class MaterialInstanceDispatcher(ChannelNotifier):
    @classmethod
    def dispatch_event(cls, material, changes, is_updated):
        changes_set = set(changes) if changes else set()
        assignment_changes = {"patient_instance", "area", "lab"}

        if changes_set - assignment_changes or not changes:
            cls._notify_exercise_update(cls.get_exercise(material))

        if changes_set & assignment_changes or not changes:
            channel = cls.get_group_name(cls.get_exercise(material))
            event = {"type": ChannelEventTypes.RESOURCE_ASSIGNMENT_EVENT}
            _notify_group(channel, event)

    @classmethod
    def create_trainer_log(cls, material, changes, is_updated):
        changes_set = set(changes) if changes else set()
        assignment_changes = {"patient_instance", "area", "lab"}

        category = models.LogEntry.CATEGORIES.MATERIAL
        type = None
        content = {"name": material.name}
        if not is_updated:
            type = models.LogEntry.TYPES.ARRIVED
            if material.area:
                content["location"] = str(material.area)
            if material.lab:
                content["location"] = str(material.lab)
            log_entry = models.LogEntry.objects.create(
                exercise=cls.get_exercise(material),
                category=category,
                type=type,
                content=content,
                is_dirty=True,
            )
            log_entry.materials.add(material)
            log_entry.set_dirty(False)
            return

        if changes_set & assignment_changes:
            type = models.LogEntry.TYPES.UNASSIGNED
            current_location = material.attached_instance()
            content["location_type"] = current_location.frontend_model_name()
            content["location_name"] = current_location.name
            log_entry = None

            if isinstance(current_location, models.PatientInstance):
                type = models.LogEntry.TYPES.ASSIGNED
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(material),
                    category=category,
                    type=type,
                    content=content,
                    patient_instance=current_location,
                    is_dirty=True,
                )
            if isinstance(current_location, models.Area):
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(material),
                    category=category,
                    type=type,
                    content=content,
                    area=current_location,
                    is_dirty=True,
                )
            if isinstance(current_location, models.Lab):
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(material),
                    category=category,
                    type=type,
                    content=content,
                    is_dirty=True,
                )
            if log_entry:
                log_entry.materials.add(material)
                log_entry.set_dirty(False)

    @classmethod
    def delete_and_notify(cls, material, *args, **kwargs):
        exercise = cls.get_exercise(material)
        super(material.__class__, material).delete(*args, **kwargs)
        cls._notify_exercise_update(exercise)

    @classmethod
    def get_exercise(cls, material):
        return cls.get_exercise_from_instance(material.attached_instance())


class PatientInstanceDispatcher(ChannelNotifier):
    location_changes = {"patient_instance", "area", "lab"}

    @classmethod
    def dispatch_event(cls, patient_instance, changes, is_updated):
        changes_set = set(changes) if changes else set()

        if changes and "patient_state" in changes:
            cls._notify_patient_state_change(patient_instance)

        if not (changes and len(changes) == 1 and "patient_state" in changes):
            cls._notify_exercise_update(cls.get_exercise(patient_instance))

        if changes and changes_set & cls.location_changes:
            cls._notify_patient_move(patient_instance)

        if changes and "triage" in changes:
            channel = cls.get_group_name(patient_instance)
            event = {"type": ChannelEventTypes.TRIAGE_UPDATE_EVENT}
            _notify_group(channel, event)

    @classmethod
    def create_trainer_log(cls, patient_instance, changes, is_updated):
        changes_set = set(changes) if changes else set()
        category = models.LogEntry.CATEGORIES.PATIENT
        type = None
        content = {"name": patient_instance.name, "code": str(patient_instance.code)}
        recall_args = None
        if not is_updated:
            type = models.LogEntry.TYPES.ARRIVED
            if (
                patient_instance.static_information
                and patient_instance.static_information.injury
            ):
                content["injuries"] = str(patient_instance.static_information.injury)
                recall_args = [patient_instance, ["patient_state"], True]
        elif changes and "triage" in changes:
            # get_triage_display gets the long version of a ChoiceField
            content["level"] = str(patient_instance.get_triage_display())
            type = models.LogEntry.TYPES.TRIAGED
        elif changes and "patient_state" in changes:
            type = models.LogEntry.TYPES.UPDATED
            content["state"] = patient_instance.patient_state.vital_signs
            content["dead"] = patient_instance.patient_state.is_dead
        elif changes and changes_set & cls.location_changes:
            type = models.LogEntry.TYPES.MOVED
            current_location = patient_instance.attached_instance()
            content["location_type"] = current_location.frontend_model_name()
            content["location_name"] = str(current_location.name)
        else:
            print(f"changes are: {changes}")
            print(f"Wird geupdated? {is_updated}")
        if content:
            if patient_instance.area:
                models.LogEntry.objects.create(
                    exercise=cls.get_exercise(patient_instance),
                    content=content,
                    category=category,
                    type=type,
                    patient_instance=patient_instance,
                    area=patient_instance.area,
                )
            else:
                models.LogEntry.objects.create(
                    exercise=cls.get_exercise(patient_instance),
                    category=category,
                    type=type,
                    content=content,
                    patient_instance=patient_instance,
                )
        if recall_args:
            cls.create_trainer_log(*recall_args)

    @classmethod
    def get_exercise(cls, patient_instance):
        return patient_instance.exercise

    @classmethod
    def _notify_patient_state_change(cls, patient_instance):
        channel = cls.get_group_name(patient_instance)
        event = {
            "type": ChannelEventTypes.STATE_CHANGE_EVENT,
            "patient_instance_pk": patient_instance.id,
        }
        _notify_group(channel, event)

    @classmethod
    def _notify_patient_move(cls, patient_instance):
        channel = cls.get_group_name(patient_instance.exercise)
        event = {
            "type": ChannelEventTypes.RESOURCE_ASSIGNMENT_EVENT,
        }
        _notify_group(channel, event)

    @classmethod
    def delete_and_notify(cls, patient, *args, **kwargs):
        exercise = patient.exercise
        super(patient.__class__, patient).delete(*args, **kwargs)
        cls._notify_exercise_update(exercise)


class PersonnelDispatcher(ChannelNotifier):
    assignment_changes = {"patient_instance", "area", "lab"}

    @classmethod
    def dispatch_event(cls, personnel, changes, is_updated):
        changes_set = set(changes) if changes else set()

        if changes_set - cls.assignment_changes or not changes:
            cls._notify_exercise_update(cls.get_exercise(personnel))

        if changes_set & cls.assignment_changes or not changes:
            channel = cls.get_group_name(cls.get_exercise(personnel))
            event = {"type": ChannelEventTypes.RESOURCE_ASSIGNMENT_EVENT}
            _notify_group(channel, event)

    @classmethod
    def create_trainer_log(cls, personnel, changes, is_updated):
        changes_set = set(changes) if changes else set()
        content = {"name": personnel.name}
        if not is_updated:
            if personnel.area:
                content["location_type"] = personnel.area.frontend_model_name()
                content["location_name"] = personnel.area.name
            if personnel.lab:
                content["location_type"] = personnel.lab.frontend_model_name()
                content["location_name"] = personnel.lab.name
            log_entry = models.LogEntry.objects.create(
                exercise=cls.get_exercise(personnel),
                category=models.LogEntry.CATEGORIES.PERSONNEL,
                type=models.LogEntry.TYPES.ARRIVED,
                content=content,
                is_dirty=True,
            )
            log_entry.personnel.add(personnel)
            log_entry.set_dirty(False)
            return

        if changes_set & cls.assignment_changes:
            current_location = personnel.attached_instance()
            content["location_type"] = current_location.frontend_model_name()
            content["location_name"] = current_location.name
            log_entry = None

            if isinstance(current_location, models.PatientInstance):
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(personnel),
                    category=models.LogEntry.CATEGORIES.PERSONNEL,
                    type=models.LogEntry.TYPES.ASSIGNED,
                    content=content,
                    patient_instance=current_location,
                    is_dirty=True,
                )
            elif isinstance(current_location, models.Area):
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(personnel),
                    category=models.LogEntry.CATEGORIES.PERSONNEL,
                    type=models.LogEntry.TYPES.UNASSIGNED,
                    content=content,
                    area=current_location,
                    is_dirty=True,
                )
            elif isinstance(current_location, models.Lab):
                log_entry = models.LogEntry.objects.create(
                    exercise=cls.get_exercise(personnel),
                    category=models.LogEntry.CATEGORIES.PERSONNEL,
                    type=models.LogEntry.TYPES.ASSIGNED,
                    content=content,
                    is_dirty=True,
                )
            if log_entry:
                log_entry.personnel.add(personnel)
                log_entry.set_dirty(False)

    @classmethod
    def delete_and_notify(cls, personnel, *args, **kwargs):
        exercise = cls.get_exercise(personnel)
        super(personnel.__class__, personnel).delete(*args, **kwargs)
        cls._notify_exercise_update(exercise)

    @classmethod
    def get_exercise(cls, personnel):
        return cls.get_exercise_from_instance(personnel.attached_instance())


class LabDispatcher(ChannelNotifier):
    @classmethod
    def get_exercise(cls, lab):
        return lab.exercise


class ViolationDispatcher:
    @classmethod
    def get_group_name(cls, session_id):
        return f"log_rules_{session_id}_log"

    @classmethod
    async def dispatch_durational_violation_started(
        cls,
        session_id,
        rule_name,
        template_name,
        violation_assignment,
        start_stamp,
        start_point,
        input_type,
    ):
        channel = cls.get_group_name(session_id)
        event = {
            "type": ChannelEventTypes.DURATIONAL_VIOLATION_START_EVENT,
            "rule_name": rule_name,
            "template_name": template_name,
            "violation_instance": violation_assignment,
            "start_stamp": start_stamp,
            "start_point": start_point,
            "input_type": input_type,
        }
        await _async_notify_group(channel, event)

    @classmethod
    async def dispatch_durational_violation_finished(
        cls,
        session_id,
        rule_name,
        template_name,
        violation_assignment,
        start_stamp,
        start_point,
        past_end_stamp,
        past_end_point,
        input_type,
    ):
        channel = cls.get_group_name(session_id)
        event = {
            "type": ChannelEventTypes.DURATIONAL_VIOLATION_END_EVENT,
            "rule_name": rule_name,
            "template_name": template_name,
            "violation_instance": violation_assignment,
            "start_stamp": start_stamp,
            "start_point": start_point,
            "past_end_stamp": past_end_stamp,
            "past_end_point": past_end_point,
            "input_type": input_type,
        }
        await _async_notify_group(channel, event)

    @classmethod
    async def dispatch_durational_violation_update(
        cls,
        session_id,
        rule_name,
        template_name,
        violation_assignment,
        time_stamp,
        time_point,
        input_type,
    ):
        channel = cls.get_group_name(session_id)
        event = {
            "type": ChannelEventTypes.DURATIONAL_VIOLATION_UPDATE_EVENT,
            "rule_name": rule_name,
            "template_name": template_name,
            "violation_assignment": violation_assignment,
            "time_stamp": time_stamp,
            "time_point": time_point,
            "input_type": input_type,
        }
        await _async_notify_group(channel, event)

    @classmethod
    async def dispatch_singular_violation(
        cls,
        session_id,
        rule_name,
        template_name,
        violation_assignment,
        time_stamp,
        time_point,
        input_type,
    ):
        channel = cls.get_group_name(session_id)
        event = {
            "type": ChannelEventTypes.SINGULAR_VIOLATION_EVENT,
            "rule_name": rule_name,
            "template_name": template_name,
            "violation_assignment": violation_assignment,
            "time_stamp": time_stamp,
            "time_point": time_point,
            "input_type": input_type,
        }
        await _async_notify_group(channel, event)

    @classmethod
    async def dispatch_processing_finished(
        cls, session_id, rule_name, template_name, input_type
    ):
        channel = cls.get_group_name(session_id)
        event = {
            "type": ChannelEventTypes.VIOLATION_PROCESSING_FINISHED,
            "rule_name": rule_name,
            "template_name": template_name,
            "input_type": input_type,
        }
        await _async_notify_group(channel, event)
