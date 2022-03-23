import numpy as np
import pandas as pd
import pathlib

class CSVLogger:
    """
    CSVLogger wraps up mundane stuff to do with creating a comma separated
    values log file
    - create the file
    - dynamically add data
    - write data to the log
    
    CSVLogger inherits from ContextManager so the file should always be saved
    in a valid state
    
    """
    
    
    
    
    def __init__(self, filepath):
        """
        on creation, check that we can write to the file
 
        TODO: handle empty filename
        TODO: handle file already exists
        """
        # print(filepath)
        self.log_path = pathlib.Path(filepath)
        self.log_path.touch(exist_ok=False)  # do NOT overwrite!
        
        self.current_row_id = []  # unique key for dataframe - probaby the trial number
        self.current_row_df = pd.DataFrame(columns=['row_id'])      # dataframe being built for the current row
        self.full_df = pd.DataFrame(columns=['row_id'])         # dataframe containing all the data
        
        self.current_row_df.set_index('row_id',inplace=True)
        self.full_df.set_index('row_id',inplace=True)

    # implement conext manager magic
    def __enter__(self):
        """
        context manager magic

        Returns
        -------
        CSVLogger
            This object provides the interface
        """
        # self.file = open(self.log_path, 'w')
        # return self.file
        return self

    # implement conext manager magic
    def __exit__(self, exc_type, exc_value, traceback):
        """
        context manager magic
        
        closes the file
        
        TODO: makes sure all data has been written
        """
        # if self.file:
        #     self.finalise_current_row()
        #     self.file.close()
        self.finalise_current_row()


    def dfs_are_consistent(self):
        """
        Checks whether the saved dataframe and the row dataframe are consistent
        
        Currently this just checks the column names but it could be extended

        Returns
        -------
        Bool: True if they are the same

        """
        return self.current_row_df.columns.equals(self.full_df.columns)
        
        

    # save data to the log
    def append(self, row_id, data, prefix=''):
        # error checking
        if (data.ndim != 2):
            raise ValueError("Expected a pandas DataFrame")
        shape = data.shape
        if (shape[0] != 1):
            raise ValueError("Expected a single row")

        # add prefix to column names just in case they get duplicated
        if (prefix != ''):
            data = data.add_prefix(prefix)
            
        # force the index of the added dataframe row
        # print(data)
        data = data.reset_index() # get rid of current index (in some cases it is called row_id)
        # data["row_id"]=row_id # causes SettingWithCopyWarning
        # print(data)
        data.loc[:,"row_id"] = row_id
        # print(data)
        data.set_index("row_id", inplace=True)
        # print(data)

        # check if we are appending to the current row or starting a new one
        if (row_id is not self.current_row_id):
            # print(self.full_df)
            if (row_id in self.full_df.index.values):
                raise ValueError('Cannot reuse row_id once row is finalised')
            self.finalise_current_row()
            self.current_row_id = row_id
            self.current_row_df = data
        else:
            # index of single row should always match
            self.current_row_df = pd.concat([self.current_row_df, data],
                                            axis=1)
    
        # sanity check
        # print(self.current_row_df)
        if (self.current_row_df.shape[0] != 1):
            raise ValueError("The concatenated dataframe isn't a row")
    
    
    # append the current row to the full log
    def finalise_current_row(self):
        # print('Entered finalise_current_row')
        # print(self.full_df)
        # print(self.current_row_df)
        
        if (self.current_row_df.shape[0] == 0):
            print('Nothing to save')
        else:       
            if self.dfs_are_consistent():
                # write row then join
                self.current_row_df.to_csv(self.log_path,
                     index=True,
                     header=False,
                     mode='a')
                self.full_df = pd.concat([self.full_df, self.current_row_df])
            else:            
                # join then overwrite full log
                self.full_df = pd.concat([self.full_df, self.current_row_df])
                self.full_df.to_csv(self.log_path,
                index=True,
                header=True,
                mode='w')

               
            
        # df_to_write.T.to_csv(self.log_path,
        #              index=False,
        #              header=False,
        #              mode='a')
 