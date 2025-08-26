Now, the Bandaskapp implements summer regime, where only DHW is needed. Lets move to phase 2, where we will add implementation of winter regime.

Update the code and settings so that the control temperature (the circuit) for DWH and HHW can be set in settings.py. Now it is hardcoded DWH -> THERMOMETER_DHW_1_ID . For the HHW, the control temperature sensor will be HHW -> THERMOMETER_HHW_1_ID. Call it CONTROL_DHW_ID and CONTROL_HHW_ID. Be cautios as the same circuit can be set to both CONTROL_DHW_ID and CONTROL_HHW_ID.

There will be one major variable setting the winter regime state. Let's call it "winter_regime_state". I expect values to be "automatic", "off", "on". There will be button in the UI cycling through the state everytime I click. The button will substitute "sync relays" button which will be moved to Setting tab. The button has label "Winter ON/AUTOMATIC/OFF"

The "winter_regime_state" == "off" regime means summer regime (only DHW). 
The "winter_regime_state" == "automatic" regime means winter regime where the pump and furnace state is controled by heating unit state. The heating unit state is sent through HW HEATING_CONTROL_UNIT_ID. The EVOK API will return json as below.
The "winter_regime_state" == "on" regime means winter regime where the pump and furnace state is controled by Bandaskapp and the pump is always on and furnace is controled to keep CONTROL_HHW_ID (representing the given thermometer) within a range. It means the pump runs continuously regardless of temperature conditions.

JSON returned by EVOK API for HEATING_CONTROL_UNIT_ID. It sits on API: http://192.168.1.2:8080/json/di/{circuit}
{
  "dev": "di",
  "circuit": "1_01",
  "value": 0,
  "debounce": 30,
  "counter_modes": [
    "Enabled",
    "Disabled"
  ],
  "counter_mode": "Enabled",
  "counter": 0,
  "mode": "Simple",
  "modes": [
    "Simple",
    "DirectSwitch"
  ]
}
The value we are interested in is "value". If "value" == 0 then heating control unit does not asks for HHW. If "value" == 1 then heating control unit does asks for HHW.

The winter regime logic:
If HEATING_CONTROL_UNIT_ID value == 0
  pump is off.
  furnace is controled just by the DHW logic as is now.
If HEATING_CONTROL_UNIT_ID value == 1
  pump is on
  furnace is controled the DHW logic AND HHW logic. There is logical OR so if any of DHW or HHW switch on the furnace, the furnace is started.

Meaning:
- If DHW needs heat OR HHW needs heat → turn furnace ON
- If both DHW AND HHW are satisfied → turn furnace OFF

The winter_regime_state default state is automatic is not needed to pe persistent across application restarts.

Do not forget to implementation the HW simulator. I expect, that the HEATING_CONTROL_UNIT_ID API will cycle in 15s intervals between ON and OFF (stay 15s in a state and then switch state). There should also manual input. Pressing "h" will cycle the HEATING_CONTROL_UNIT_ID. 

I expect following steps:
1. put settings of control circuits into the config
2. update the simulator
3. implement the rest

The temperature thresholds DHW and HHW highs/lows has to be persistent and should be saved/restored when app restarts. When initialized, HHW thresholds will share the same values as DHW. It is low=45 high=60.

Error Handling: How should the system behave if the heating control unit API is unreachable or returns an error? Then switch the mode to manual and let human user to set the furnace / pump manualy. Until the mode is not switched back to automatic by human.

Transition Behavior: When switching between winter regime states, should there be any delay or safety checks before changing the pump/furnace behavior? Not needed.

Manual Mode: In manual mode (when API errors occur), should the user be able to control both pump and furnace independently, or are there any constraints? Both independenty as it is now in the UI. Meaning 2 separated buttons.

API Polling Frequency: How often should the system poll the heating control unit API to check for state changes? The same as for DHW now for the thermometers.
