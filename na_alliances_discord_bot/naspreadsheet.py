import json
import logging

import aiohttp
import gspread

from util import LoggingClientSession

class NAGuildSpreadSheet:
    def __init__(self,
                 client: gspread.Client,
                 spreadsheet_url: str):
        self.logger = logging.getLogger(__name__)
        self.client = client
        if 'https' in spreadsheet_url:
            self.sheet = client.open_by_url(spreadsheet_url)
        else:
            self.sheet = client.open_by_key(spreadsheet_url)
        
    def convert_boolean(self, var: str) -> bool:
        if var == "TRUE":
            return True
        elif var == "FALSE":
            return False
        else:
            return var

    def get_sheet_data(self) -> dict:
        self.logger.info("Getting Spreadsheet Data")
        data = {}
        for ws in self.sheet.worksheets():
            if ws.title not in ["Alliances", "SoloGuilds"]:
                continue
            self.logger.debug(f"Requesting data for worksheet: {ws.title}")
            name = ws.title
            self.logger.debug(ws.get("A1:V1"))
            try:
                d = ws.get_all_values()
                out = []
                headers = d[0]
                for r in d[1:]:
                    if '[' not in r[0]: 
                        self.logger.debug(f"ignoring {r}")
                        continue
                    row = [self.convert_boolean(x) for x in r]
                    out.append(dict(zip(headers, row)))
                data[name] = out
            except gspread.exceptions.GSpreadException:
                continue
        return data
