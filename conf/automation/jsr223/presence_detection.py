from custom.helper import log, rule, itemLastUpdateOlderThen, getNow, getItemState, postUpdate, sendNotification
from core.triggers import ItemStateChangeTrigger


@rule("presence_detection.py")
class PresenceCheckRule:
    def __init__(self):
        self.triggers = [
            ItemStateChangeTrigger("State_Holger_Presence"),
            ItemStateChangeTrigger("State_Sandra_Presence")
        ]
        
    def execute(self, module, input):
        itemName = input['event'].getItemName()
        itemState = input['event'].getItemState()
        
        sendNotification(u"{}".format(itemName), u"{}".format(itemState))
        
        holgerPhone = itemState if itemName == "State_Holger_Presence" else getItemState("State_Holger_Presence")
        sandraPhone = itemState if itemName == "State_Sandra_Presence" else getItemState("State_Sandra_Presence")
        
        if holgerPhone == ON or sandraPhone == ON:
            # only possible if we are away
            if getItemState("State_Presence").intValue() == 0:
                postUpdate("State_Presence",1)
                sendNotification(u"Tür", u"Willkommen")
        else:
            # only possible if we are present and not sleeping
            if getItemState("State_Presence").intValue() == 1:
                postUpdate("State_Presence",0)
                lightMsg = u" - LICHT an" if getItemState("Lights_Indoor") != OFF else u""
                windowMsg = u" - FENSTER offen" if getItemState("Openingcontacts") != CLOSED else u""

                sendNotification(u"Tür", u"Auf Wiedersehen{}{}".format(lightMsg,windowMsg))

@rule("presence_detection.py")
class WakeupRule:
    def __init__(self):
        self.triggers = [
            #ItemStateChangeTrigger("Motiondetector_FF_Floor",state="OPEN"),
            #ItemStateChangeTrigger("Motiondetector_FF_Livingroom",state="OPEN"),
            #ItemStateChangeTrigger("Motiondetector_SF_Floor",state="OPEN"),
            ItemStateChangeTrigger("Lights_FF",state="ON"),
            ItemStateChangeTrigger("Shutters_FF",state="0")
        ]

    def execute(self, module, input):        
        # only possible if we are sleeping
        if getItemState("State_Presence").intValue() == 2:
            # sometimes the "Lights_FF" state switches back and forth for a couple of milliseconds when set "Lights_FF" state to OFF
            if itemLastUpdateOlderThen("State_Presence",getNow().minusSeconds(5)):
                postUpdate("State_Presence", 1)
                sendNotification(u"System", u"Guten Morgen")

@rule("presence_detection.py") 
class SleepingRule:
    def __init__(self):
        self.triggers = [ ItemStateChangeTrigger("Scene4",state="ON") ]

    def execute(self, module, input):
        # only possible if we are present
        if getItemState("State_Presence").intValue() == 1:
            postUpdate("State_Presence", 2)
            
        postUpdate("Scene4", OFF)

log.info(u"{}".format(PercentType.ZERO))
log.info(u"{}".format(getItemState("Shutters_FF")))