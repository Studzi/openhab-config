from custom.helper import rule, getNow, itemLastUpdateOlderThen, sendNotification, getItemState, postUpdateIfChanged
from core.triggers import CronTrigger, ItemStateChangeTrigger


@rule("values_error_messages.py")
class ValuesErrorMessagesRule:
    def __init__(self):
        self.triggers = [
            CronTrigger("0 */5 * * * ?"),
            ItemStateChangeTrigger("Ventilation_Filter_Error_I"),
            ItemStateChangeTrigger("Ventilation_Filter_Error_E"),
            ItemStateChangeTrigger("Ventilation_Error_Message"),
            ItemStateChangeTrigger("Heating_Common_Fault"),
            ItemStateChangeTrigger("State_Server")
        ]

    def execute(self, module, input):
        group = u"Fehler"
        active = []

        if getItemState("Ventilation_Filter_Error_I").intValue() > 0 \
                or getItemState("Ventilation_Filter_Error_E").intValue() > 0 \
                or getItemState("Ventilation_Error_Message").toString() != "Ok":
            active.append(u"Lüftung")

        if getItemState("Heating_Common_Fault").intValue() > 0:
            active.append(u"Heizung")

        if getItemState("State_Server").intValue() > 1:
            active.append(u"Server")

        refDate = getNow().minusMinutes(1440)  # last 24 hours

        if itemLastUpdateOlderThen("Temperature_FF_Livingroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_Boxroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_Guestroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_GuestWC", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_Floor", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_Utilityroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_FF_Garage", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Bedroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Dressingroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Child1", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Child2", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Bathroom", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Floor", refDate) \
                or itemLastUpdateOlderThen("Temperature_SF_Attic", refDate):
            active.append("Sensors")

        if len(active) == 0:
            active.append(u"Alles normal")
            group = u"Info"

        msg = u", ".join(active)

        if postUpdateIfChanged("MainStatus", msg):
            sendNotification(group, msg)
