connections= [
    {
      "from": "pico:GP26",
      "to": "ph_sensor:VCC",
      "color": "red"
    },
    {
      "from": "pico:GP27",
      "to": "ph_sensor:SIG",
      "color": "yellow"
    },
    {
      "from": "pico:GND",
      "to": "ph_sensor:GND",
      "color": "black"
    },
    {
      "from": "pico:GP0",
      "to": "acid_pump:IN",
      "color": "green"
    },
    {
      "from": "pico:GP1",
      "to": "base_pump:IN",
      "color": "blue"
    },
    {
      "from": "pico:GP2",
      "to": "mixer:SIG",
      "color": "orange"
    },
    {
      "from": "pico:GP3",
      "to": "water_pump:IN",
      "color": "green"
    },
    {
      "from": "pico:GP4",
      "to": "valve1:1",
      "color": "purple"
    },
    {
      "from": "pico:GP5",
      "to": "valve2:1",
      "color": "purple"
    },
    {
      "from": "pico:GND",
      "to": "acid_pump:GND",
      "color": "black"
    },
    {
      "from": "pico:GND",
      "to": "base_pump:GND",
      "color": "black"
    },
    {
      "from": "pico:GND",
      "to": "mixer:GND",
      "color": "black"
    },
    {
      "from": "pico:GND",
      "to": "water_pump:GND",
      "color": "black"
    },
    {
      "from": "pico:GND",
      "to": "valve1:2",
      "color": "black"
    },
    {
      "from": "pico:GND",
      "to": "valve2:2",
      "color": "black"
    }
] 

new_connections = [ ]
for connection in connections:
    new_connections.append([str(connection["from"]),connection["to"],connection["color"]])
print(new_connections)