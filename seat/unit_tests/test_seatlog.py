import shutil, tempfile
import pathlib
import unittest
import pandas as pd
import pandas.testing as pd_testing
from seatlog import CSVLogger



class TestSeatLog(unittest.TestCase):
    # test of DataFrame from https://stackoverflow.com/a/54344148/3041762
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

            
    def assertSeriesEqual(self, a, b, msg):
        try:
            pd_testing.assert_series_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e  

            
    def setUp(self):
        
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)
        self.addTypeEqualityFunc(pd.Series, self.assertSeriesEqual)
        
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        # print(self.test_dir)
        

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

        
    def test_fails_on_file_exists(self):
        """
        Test that if file already exists it errors out
        """
        # populate it with a file
        self.preexisting_file = pathlib.Path(self.test_dir,'existing_file.csv')
        self.preexisting_file.touch();
        log_path = self.preexisting_file
        self.assertRaises(Exception, CSVLogger, log_path)


    def test_single_frame(self):
        """
        Write one line to file
        """
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df = pd.DataFrame([[1, 'A']], columns=['col_1_int','col_2_str'])
        
        # truth
        true_df = pd.DataFrame([[row_id, 1, 'A']], columns=['row_id','col_1_int','col_2_str'])
        
        # code under test        
        with CSVLogger(log_path) as mylogger:
            mylogger.append(row_id, df)
        
        # read it back in and check
        in_df = pd.read_csv(log_path)
        
        # print('original')
        # print(true_df)
        # print('saved')
        # print(in_df)       
        
        self.assertEqual(in_df, true_df)


    def test_two_frames(self):
        """
        Write one line to file from two frames
        """
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df = pd.DataFrame([[1, 'A']], columns=['col_1_int','col_2_str'])
        df2 = pd.DataFrame([['bob', 0, 1, 0, 0, 1]],
                           columns=['col_3_str','col_4_bool_1',
                                        'col_4_bool_2','col_4_bool_3',
                                        'col_4_bool_4','col_4_bool_5'])
        # truth
        true_df = pd.DataFrame([[row_id, 1, 'A', 'bob', 0, 1, 0, 0, 1]],
                               columns=['row_id','col_1_int','col_2_str',
                                        'col_3_str','col_4_bool_1',
                                        'col_4_bool_2','col_4_bool_3',
                                        'col_4_bool_4','col_4_bool_5'])
  
        
        # code under test        
        with CSVLogger(log_path) as mylogger:
            mylogger.append(row_id, df)
            mylogger.append(row_id, df2)
        
        # read it back in and check
        in_df = pd.read_csv(log_path)
        
        # print('original')
        # print(true_df)
        # print(true_df.dtypes)
        # print(type(true_df['col_4_bool_1'].iat[0]))
        # print('saved')
        # print(in_df)       
        # print(in_df.dtypes)
        # print(type(in_df['col_4_bool_1'].iat[0]))
   
        self.assertEqual(in_df, true_df)


    def test_two_rows(self):
        """
        Write two lines
        """
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df = pd.DataFrame([[1, 'A']], columns=['col_1_int','col_2_str'])
        row_id2 = 14
        df2 = pd.DataFrame([[2, 'B']], columns=['col_1_int','col_2_str'])
       
        # truth
        # true_df = pd.DataFrame([[row_id, row_id2], [1, 2], ['A', 'B']],
        #                        columns=['row_id','col_1_int','col_2_str'])
        true_df = pd.DataFrame([[row_id, 1, 'A'], [row_id2, 2, 'B']],
                               columns=['row_id','col_1_int','col_2_str'])
  
        
        # code under test        
        with CSVLogger(log_path) as mylogger:
            mylogger.append(row_id, df)
            mylogger.append(row_id2, df2)
        
        # read it back in and check
        in_df = pd.read_csv(log_path)
        
        # print('original')
        # print(true_df)
        # print('saved')
        # print(in_df)       
 
        self.assertEqual(in_df, true_df)


    def test_two_frames_two_rows(self):
        """
        Write two lines
        """
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df_11 = pd.DataFrame([[1, 'A']], columns=['col_1_int','col_2_str'])
        df_12 = pd.DataFrame([[11, 'AA']], columns=['col_3_int','col_4_str'])
        
        row_id2 = 14
        df_21 = pd.DataFrame([[2, 'B']], columns=['col_1_int','col_2_str'])
        df_22 = pd.DataFrame([[22, 'BB']], columns=['col_3_int','col_4_str'])
       
        # truth
        true_df = pd.DataFrame([[row_id, 1, 'A', 11, 'AA'],
                                [row_id2, 2, 'B', 22, 'BB']],
                               columns=['row_id','col_1_int','col_2_str',
                                        'col_3_int','col_4_str'])
  
        
        # code under test        
        with CSVLogger(log_path) as mylogger:
            # first row
            mylogger.append(row_id, df_11)
            mylogger.append(row_id, df_12)
            # second row  , n.b. order is reversed       
            mylogger.append(row_id2, df_22)
            mylogger.append(row_id2, df_21)
            
        
        # read it back in and check
        in_df = pd.read_csv(log_path)
        
        # print('original')
        # print(true_df)
        # print('saved')
        # print(in_df)       
   
        self.assertEqual(in_df, true_df)


    def test_non_unique_row_id(self):
        """
        Write two lines
        """
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df_11 = pd.DataFrame([[1, 'A']], columns=['col_1_int','col_2_str'])
        df_12 = pd.DataFrame([[11, 'AA']], columns=['col_3_int','col_4_str'])
        
        row_id2 = 14
        df_22 = pd.DataFrame([[22, 'BB']], columns=['col_3_int','col_4_str'])

    
        # code under test        
        with CSVLogger(log_path) as mylogger:
            # first row
            mylogger.append(row_id, df_11)
            # second row
            mylogger.append(row_id2, df_22)
            # first row again
            self.assertRaises(Exception, mylogger.append, row_id, df_12)

       
    def test_two_rows_in_one_call_fails(self):
        # setup data      
        log_path = pathlib.Path(self.test_dir,'new_file.csv')
        row_id = 0
        df_11 = pd.DataFrame([[1], [2]], columns=['col_1_int'])
        # print(df_11)

        # code under test        
        with CSVLogger(log_path) as mylogger:
            self.assertRaises(Exception, mylogger.append, row_id, df_11)

if __name__ == '__main__':
    unittest.main()
