# na-alliances-discord-bot
 
Use neven's spreadsheet to update the NA Alliances Discord.

## Config

```json
{
    "token": "<discord token>",
    "db": "na_alliances_discord.sqlite",
    "channels": {
        "discord server name": [
            "discord channel name"
        ]
    },
    "storage_channel": {
        "discord server name": "discord channel name"
    },
    "servers": {
        "AP": "Abaddon's Prison",
        "DoT": "Domain of Torment",
        "DT": "Dwayna's Temple",
        "HoJ": "Hall of Judgement",
        "LC": "Lutgardis Conservatory",
        "Moogooloo": "Moogooloo",
        "MW": "Mosswood",
        "RR": "Rall's Rest",
        "CoB": "Cathedral of Blood",
        "ThroB": "Throne of Balthazar",
        "ToD": "Tombs of Drascir",
        "YH": "Yohlon Haven"
    },
    "google_service_account": {"<json block for a service account>": true},
    "google_spreadsheet_id": "1Txjpcet-9FDVek6uJ0N3OciwgbpE0cfWozUK7ATfWx4"
}
```