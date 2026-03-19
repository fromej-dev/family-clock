# Family Clock for Home Assistant

A Weasley-style enchanted family clock — each member has a clock hand pointing to their current activity. Schedule is stored in Home Assistant and shared across all devices.

## Installation via HACS

1. In HACS → go to **Integrations** → click the three-dot menu → **Custom repositories**
2. Add your repository URL, category: **Integration**
3. Install **Family Clock**
4. Restart Home Assistant

## Manual Installation

1. Copy the `custom_components/family_clock/` folder into your HA `config/custom_components/` directory
2. Copy the `www/family-clock.html` file into your HA `config/www/family_clock/` directory  
   (create the `family_clock` subfolder if it doesn't exist)
3. Add to your `configuration.yaml`:
   ```yaml
   family_clock:
   ```
4. Restart Home Assistant
5. The clock appears in your sidebar as **Family Clock**

## Dashboard Card

Add the Family Clock to any Lovelace dashboard using the custom card type:

```yaml
type: custom:family-clock-card
```

The card is automatically registered when the integration loads — no manual resource configuration needed.

**Optional config:**

| Key | Default | Description |
|-----|---------|-------------|
| `height` | `800px` | Card height (any valid CSS value) |

Example with custom height:

```yaml
type: custom:family-clock-card
height: 1000px
```

You can also find it in the card picker UI by searching for "Family Clock".

## Members

Default members are EJ, Ilona, Femke, Nynke. Edit via the ⚙ button inside the clock — names are saved to HA storage.

## Activities

- Home Work
- Office Work  
- Head Office
- Home Day Kids
- Playdate
- School Long
- School Short
- BSO
- Swimming Lesson
- Gym Lesson

## Home Assistant Sensor Integration (future)

The clock exposes `window.familyClockSetLocation(memberName, activityId)` so HA automations can push location/activity updates directly.

Activity IDs: `homework`, `officework`, `headoffice`, `homeday`, `playdate`, `schoollong`, `schoolshort`, `bso`, `swimming`, `gym`

Example automation using a `browser_mod` service call:
```yaml
automation:
  - alias: "EJ arrives at office"
    trigger:
      - platform: state
        entity_id: person.ej
        to: "Office"
    action:
      - service: browser_mod.javascript
        data:
          code: "window.familyClockSetLocation('EJ', 'officework')"
```

## API

The integration exposes a REST endpoint at `/api/family_clock/schedule`:

- `GET /api/family_clock/schedule` — returns `{ schedule, members }`
- `POST /api/family_clock/schedule` — saves `{ schedule, members }`

All requests require a valid HA auth token.
