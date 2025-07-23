from fastapi import Request
import pandas as pd

class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.trans_date_trans_time: str
        self.dob: str
        self.amt: str
        self.city_pop: str
        self.merch_long: str

        
    async def get_usvisa_data(self):
        form = await self.request.form()
        self.trans_date_trans_time = form.get("trans_date_trans_time")
        self.dob = form.get("dob")
        self.amt = form.get("amt")
        self.city_pop = form.get("city_pop")
        self.merch_long = form.get("merch_long")
        
    async def get_usvisa_input_data_frame(self):
        await self.get_usvisa_data()
        data = {
            "trans_date_trans_time": [self.trans_date_trans_time],
            "dob": [self.dob],
            "amt": [self.amt],
            "city_pop": [self.city_pop],
            "merch_long": [self.merch_long]
        }
        
        return pd.DataFrame(data)
    
    
