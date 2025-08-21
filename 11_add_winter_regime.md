Now, the Bandaskapp implements summer regime, where only DHW is needed. Lets move to phase 2, where we will add implementation of winter regime.

There will be one major variable setting the winter regime state. Let's call it "winter_regime_state". I expect values to be "automatic", "off", "on". There will be button in the UI cycling through the state everytime I click. The button will substitute "sync relays" button which will be moved to Setting tab.

The "winter_regime_state" == "off" regime means summer regime (only DHW). 
The "winter_regime_state" == "automatic" regime means winter regime where the pump and furnace state is controled by heating unit state. The heating unit state is sent through HW HEATING_CONTROL_UNIT_ID. The EVOK API will return json as below.
The "winter_regime_state" == "on" regime means winter regime where the pump and furnace state is controled by Bandaskapp and the pump is always on and furnace is controled to keep THERMOMETER_HHW_1_ID within range XXX


  



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

