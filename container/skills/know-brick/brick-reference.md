# Brick Schema Reference

Version: 1.4 | Namespace: `https://brickschema.org/schema/Brick#` | Prefix: `brick:`

## Core Class Hierarchy

### Equipment
```
Equipment
├── HVAC_Equipment
│   ├── AHU (Air Handling Unit)
│   ├── VAV (Variable Air Volume Box)
│   ├── FCU (Fan Coil Unit)
│   ├── CRAC (Computer Room Air Conditioning)
│   ├── Fan (Supply_Fan, Return_Fan, Exhaust_Fan, Relief_Fan)
│   ├── Pump (Chilled_Water_Pump, Hot_Water_Pump, Condenser_Water_Pump)
│   ├── Chiller (Centrifugal_Chiller, Absorption_Chiller)
│   ├── Boiler (Gas_Boiler, Electric_Boiler)
│   ├── Heat_Exchanger (Condenser, Evaporator)
│   ├── Cooling_Tower
│   ├── Damper (Supply_Damper, Return_Damper, Exhaust_Damper, Outside_Damper)
│   ├── Valve (Chilled_Water_Valve, Hot_Water_Valve, Bypass_Valve)
│   ├── Coil (Cooling_Coil, Heating_Coil)
│   ├── Compressor
│   ├── Filter
│   ├── Humidifier / Dehumidifier
│   ├── Heat_Pump
│   ├── Terminal_Unit
│   └── HRV / ERV (Heat/Energy Recovery Ventilator)
├── Electrical_Equipment
│   ├── Transformer
│   ├── Switchgear
│   ├── Inverter (Solar_Inverter)
│   ├── Battery / Energy_Storage
│   └── EV_Charging_Station
├── Lighting_Equipment
│   ├── Luminaire
│   └── Lighting_Driver
├── Meter
│   ├── Electrical_Meter (Building_Electrical_Meter, Panel_Electrical_Meter)
│   ├── Gas_Meter
│   ├── Water_Meter (Chilled_Water_Meter, Hot_Water_Meter)
│   └── Thermal_Power_Meter
├── Solar_Panel
├── Water_Heater (Electric_Water_Heater, Gas_Water_Heater)
└── ICT_Equipment (Server, Controller, Gateway)
```

### Point (data points — sensors, commands, setpoints)
```
Point
├── Sensor
│   ├── Temperature_Sensor
│   │   ├── Air_Temperature_Sensor (Zone_Air_Temperature_Sensor, Supply_Air_Temperature_Sensor,
│   │   │   Return_Air_Temperature_Sensor, Outside_Air_Temperature_Sensor,
│   │   │   Discharge_Air_Temperature_Sensor, Mixed_Air_Temperature_Sensor)
│   │   ├── Water_Temperature_Sensor (Chilled_Water_Temperature_Sensor,
│   │   │   Hot_Water_Temperature_Sensor, Entering/Leaving_Water_Temperature_Sensor)
│   │   └── Soil_Temperature_Sensor
│   ├── Humidity_Sensor (Relative_Humidity_Sensor, Zone/Outside/Return/Supply_Air_Humidity_Sensor)
│   ├── Pressure_Sensor (Static_Pressure_Sensor, Differential_Pressure_Sensor)
│   ├── Flow_Sensor (Air_Flow_Sensor, Water_Flow_Sensor, Supply/Return_Air_Flow_Sensor)
│   ├── CO2_Sensor (Zone_CO2_Sensor)
│   ├── Occupancy_Sensor / People_Count_Sensor
│   ├── Power_Sensor / Energy_Sensor
│   ├── Voltage_Sensor / Current_Sensor
│   ├── Speed_Sensor
│   └── Illuminance_Sensor
├── Setpoint
│   ├── Temperature_Setpoint (Zone_Air_Temperature_Setpoint, Cooling/Heating_Temperature_Setpoint,
│   │   Supply_Air_Temperature_Setpoint, Occupied/Unoccupied/Standby_*_Setpoint)
│   ├── Pressure_Setpoint (Static_Pressure_Setpoint)
│   ├── Flow_Setpoint (Supply_Air_Flow_Setpoint)
│   ├── Humidity_Setpoint
│   └── Speed_Setpoint
├── Command
│   ├── On_Off_Command (Fan_On_Off_Command, Pump_On_Off_Command)
│   ├── Frequency_Command
│   ├── Speed_Command (Fan_Speed_Command)
│   ├── Position_Command (Damper_Position_Command, Valve_Position_Command)
│   ├── Mode_Command (Cooling/Heating/Occupied_Mode_Command)
│   └── Enable_Command / Disable_Command
├── Status
│   ├── On_Off_Status (Fan_On_Off_Status, Pump_On_Off_Status)
│   ├── Mode_Status (Occupancy_Mode_Status, Cooling/Heating_Mode_Status)
│   ├── Fault_Status
│   ├── Run_Status
│   └── Speed_Status
├── Alarm
│   ├── Temperature_Alarm (High/Low_Temperature_Alarm)
│   ├── Pressure_Alarm
│   ├── Humidity_Alarm
│   └── CO2_Alarm
└── Parameter
    ├── Delay_Parameter
    ├── Deadband_Parameter
    ├── Proportional_Band_Parameter
    └── Integral_Time_Parameter
```

### Location (spatial hierarchy)
```
Location
├── Site
├── Building
├── Floor (Basement, Roof)
├── Room (Office, Conference_Room, Laboratory, Server_Room, Mechanical_Room, Electrical_Room)
├── Space
├── Wing
├── Zone (HVAC_Zone, Lighting_Zone, Fire_Zone)
└── Outdoor_Area
```

## Key Relationships

| Relationship | Inverse | Use |
|-------------|---------|-----|
| `feeds` | `isFedBy` | Equipment/system flow: AHU feeds VAV |
| `hasPoint` | `isPointOf` | Equipment to data points: AHU hasPoint SAT_Sensor |
| `isPartOf` | `hasPart` | Composition: Room isPartOf Floor |
| `isLocationOf` | `hasLocation` | Spatial: Room isLocationOf Sensor |
| `controls` | `isControlledBy` | Control: Controller controls Equipment |
| `meters` | `isMeteredBy` | Metering: Meter meters Equipment |
| `hasSubMeter` | `isSubMeterOf` | Meter hierarchy |

## Common SPARQL Queries

### All equipment with their points
```sparql
SELECT ?equip ?equip_type ?point ?point_type WHERE {
    ?equip a ?equip_type .
    ?equip_type rdfs:subClassOf* brick:Equipment .
    ?equip brick:hasPoint ?point .
    ?point a ?point_type .
}
```

### Full feed chain (what feeds what)
```sparql
SELECT ?upstream ?downstream WHERE {
    ?upstream brick:feeds+ ?downstream .
}
```

### All sensors in a zone with their equipment
```sparql
SELECT ?zone ?equip ?sensor ?sensor_type WHERE {
    ?zone a brick:HVAC_Zone .
    ?equip brick:feeds ?zone .
    ?equip brick:hasPoint ?sensor .
    ?sensor a ?sensor_type .
    ?sensor_type rdfs:subClassOf* brick:Sensor .
}
```

### Spatial hierarchy
```sparql
SELECT ?building ?floor ?room WHERE {
    ?room a brick:Room .
    ?room brick:isPartOf ?floor .
    ?floor a brick:Floor .
    ?floor brick:isPartOf ?building .
    ?building a brick:Building .
}
```

### Equipment in a specific location
```sparql
SELECT ?equip ?equip_type WHERE {
    ?equip a ?equip_type .
    ?equip_type rdfs:subClassOf* brick:Equipment .
    ?equip brick:hasLocation ?loc .
    ?loc a brick:Mechanical_Room .
}
```

### Temperature sensors with their measurement context
```sparql
SELECT ?sensor ?sensor_type ?equip WHERE {
    ?sensor a ?sensor_type .
    ?sensor_type rdfs:subClassOf* brick:Temperature_Sensor .
    ?sensor brick:isPointOf ?equip .
}
```

### All meters and what they measure
```sparql
SELECT ?meter ?meter_type ?target ?target_type WHERE {
    ?meter a ?meter_type .
    ?meter_type rdfs:subClassOf* brick:Meter .
    ?meter brick:meters ?target .
    ?target a ?target_type .
}
```

## BMS Point Mapping Guide

When mapping BMS/BAS point names to Brick classes, use this pattern:

| BMS Pattern | Brick Class |
|-------------|-------------|
| `SAT`, `SupplyAirTemp` | `Supply_Air_Temperature_Sensor` |
| `RAT`, `ReturnAirTemp` | `Return_Air_Temperature_Sensor` |
| `OAT`, `OutsideAirTemp` | `Outside_Air_Temperature_Sensor` |
| `DAT`, `DischargeAirTemp` | `Discharge_Air_Temperature_Sensor` |
| `MAT`, `MixedAirTemp` | `Mixed_Air_Temperature_Sensor` |
| `ZAT`, `ZoneTemp`, `RoomTemp` | `Zone_Air_Temperature_Sensor` |
| `RH`, `Humidity` | `Relative_Humidity_Sensor` |
| `CO2` | `CO2_Sensor` |
| `SAF`, `SupplyAirFlow` | `Supply_Air_Flow_Sensor` |
| `SP`, `StaticPressure` | `Static_Pressure_Sensor` |
| `DmprCmd`, `DamperPos` | `Damper_Position_Command` |
| `VlvCmd`, `ValvePos` | `Valve_Position_Command` |
| `FanSpd`, `FanSpeed` | `Fan_Speed_Command` |
| `FanStatus`, `FanSts` | `Fan_On_Off_Status` |
| `CoolingSP`, `ClgSP` | `Cooling_Temperature_Setpoint` |
| `HeatingSP`, `HtgSP` | `Heating_Temperature_Setpoint` |
| `OccSts`, `Occupancy` | `Occupancy_Status` |
| `kW`, `Power` | `Power_Sensor` |
| `kWh`, `Energy` | `Energy_Sensor` |
