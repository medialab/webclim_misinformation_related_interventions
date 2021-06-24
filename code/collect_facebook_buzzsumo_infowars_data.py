import os
from datetime import date

from dotenv import load_dotenv

from utils import collect_buzzsumo_data_for_one_domain


if __name__=="__main__":

    load_dotenv()
    collect_buzzsumo_data_for_one_domain(
        domain='infowars.com', 
        token=os.getenv('BUZZSUMO_TOKEN'),
        output_path=os.path.join('.', 'data', 'facebook_buzzsumo_infowars_' + str(date.today()) + '.csv'),
        begin_date='2019-01-01', 
        end_date='2021-06-15'
    )
