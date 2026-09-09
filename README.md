# Xiaomi Mi Smart Standing Fan 1C for Home Assistant

Local Home Assistant integration for Xiaomi Mi Smart Standing Fan 1C
(`dmaker.fan.1c`). It talks directly to the fan over the local network and does
not require the Xiaomi cloud during normal operation.

## Product

[![Xiaomi Mi Smart Standing Fan 1C](https://i01.appmifile.com/webfile/globalimg/xm_event/fr/0879a0c00e25cb2c29f3c6d1289ccd6e.jpg)](https://www.mi.com/it/mi-smart-standing-fan-1c/)

The image links to the [official Xiaomi product page for Mi Smart Standing Fan 1C](https://www.mi.com/it/mi-smart-standing-fan-1c/). The image is hosted on Xiaomi's `appmifile.com` content network.

## Functions

- Power control
- Three speed levels exposed as a percentage
- Normal and natural wind modes
- Oscillation
- Indicator light
- Buzzer
- Child lock
- Delayed shutoff timer from 0 to 480 minutes

## Installation

### HACS

1. Open HACS and add this repository as a custom repository of type
   `Integration`.
2. Download `Xiaomi Mi Smart Standing Fan 1C`.
3. Restart Home Assistant.

### Manual installation

Copy `custom_components/pedestal_fan_1c` to the `custom_components` directory in
your Home Assistant configuration, then restart Home Assistant.

## Configuration

1. Give the fan a fixed IP address using a DHCP reservation in your router.
2. Obtain the 32-character Xiaomi device token.
3. In Home Assistant, open **Settings > Devices & services > Add integration**.
4. Select **Xiaomi Mi Smart Standing Fan 1C** and enter the IP address and token.

The fan and Home Assistant host must be able to reach each other on the local
network. If setup fails, first check the IP address, token, and VLAN or firewall
rules.

## Supported device

| Product | Xiaomi model |
| --- | --- |
| Mi Smart Standing Fan 1C | `dmaker.fan.1c` |

## License

MIT
