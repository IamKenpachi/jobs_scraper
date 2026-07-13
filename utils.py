import pandas as pd
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def export_jobs_to_csv(jobs_list, source_site):
    """
    Exports a list of jobs directly to a timestamped CSV file in the output directory.
    """
    if not jobs_list:
        return
    
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"output/{source_site}_{timestamp}.csv"
    
    try:
        df = pd.DataFrame(jobs_list)
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(jobs_list)} jobs to {filename}")
    except Exception as e:
        logger.error(f"Failed to export CSV for {source_site}: {e}")
