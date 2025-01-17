import glob as gb
import os
import warnings
import pandas as pd
import xlwings as xw # Xlwings is a Python library that makes it easy to call Python from Excel
# used to filter out warning messages generated by modules or functions called in your code.
warnings.filterwarnings("ignore")

# function to get beps report in csv format based on conditions and allot them with columns from sim file.
# First the report is in string format, it is converted into the lists and then dataframe to print csvs
def get_BEPS_report(name):
    # Open the file named 'name' and read its contents
    with open(name) as f:
         # Read all lines from the file and store them in a list named flist
        flist = f.readlines()

        # initialize an empty list to store line from BEPS occur till BEPU start.
        beps_count = [] 
        # Iterate through each line in flist along with its line number
        for num, line in enumerate(flist, 0):
            # If 'BEPS' is in the line, append its line number to lvb_count list
            if 'BEPS' in line:
                beps_count.append(num)
            # If 'BEPU' is in the line, store its line number as numend
            if 'BEPU' in line:
                numend = num
        # Store the line number of the first occurance of BEPS
        numstart = beps_count[0] 
        # Slice flist from the start of 'BEPS' to the line before 'BEPU' and store it in beps_rpt
        beps_rpt = flist[numstart:numend]

        beps_str = []  # List to store lines containing 'MBTU'
        other_str = []  # List to store lines preceding the 'MBTU' lines
        prev_line = None  # Initialize variable to store the previous line

        # Iterate through each line in beps_rpt
        for line in beps_rpt:
            if prev_line:
                if ('MBTU' in line and '.' in line and 'TOTAL' not in line):
                    beps_str.append(line)  # Append the current line
                    other_str.append(prev_line)  # Store the previous line
            # Store the current line as the previous line for the next iteration
            prev_line = line
        
        # result list to store filtered columns. after 13th column from last remaining values in 1 column.
        result = [] 
        for line in beps_str:
            beps_list = []
            # Split the line by whitespace and store the result in splitter
            splitter = line.split()
            # Join the first part of the splitter except the last 13 elements and store it as space_name
            space_name = " ".join(splitter[:-13])
            # Add space_name as the first element of beps_list
            beps_list=splitter[-13:]
            # Add space_name as the first element of beps_list
            beps_list.insert(0,space_name)
            # append beps_list to result
            result.append(beps_list)
        # store result to dataframe
        beps_df = pd.DataFrame(result)
        
        # this list is to stores the previous line of beps source in other_result list. It will be added in
        # 1st column of the dataframe.
        other_result = []
        # iterate in other_str for each line and store other_list []
        for line in other_str:
            other_list = []
            splitter = line.split()
            # we have only 1 column. store in a list for one column.
            space_name = " ".join(splitter[:1])
            other_list=splitter[1:]
            # insert space_name as the first column of beps_df
            other_list.insert(0,space_name)
            # append other_list to other_result list.
            other_result.append(other_list)
        # store other_result to dataframe
        other_df = pd.DataFrame(other_result)
        # add value as total last row, 1st column.
        other_df.iloc[-1, 0] = 'TOTAL'

        # consider the values which are not none
        merged_column = other_df.apply(lambda x: ' '.join(str(val) for val in x if val is not None), axis=1)

        other_df = pd.DataFrame({'': merged_column})
        # adding other_df and beps_df into 1 dataframe.
        beps_df = pd.concat([other_df, beps_df], axis=1)

        # alloting columns name to each columns
        beps_df.columns = ['BEPS-SOURCE', 'BEPS-UNIT', 'LIGHTS', 'TASK-LIGHTS', 'MISQ-EQUIP', 'SPACE-HEATING',
                            'SPACE-COOLING', 'HEAT-REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRING-DISPLAY',
                            'HT-PUMP-SUPPLEMENT', 'DOMEST-HOT-WTR', 'EXT-USAGE', 'TOTAL']
        
        # sets the name of the index of the DataFrame beps_df to the value stored in the variable name.
        beps_df.index.name = name
        # reverse the path, and store value before 1st backslash occur.
        value_before_backslash = ''.join(reversed(name)).split("\\")[0]
        # after reverse store into a variable
        name1 = ''.join(reversed(value_before_backslash))
        # take the value before '.' as 1st column values.
        name = name1.rsplit(".", 1)[0]
        # insert name as column name 'RUNNAME'
        beps_df.insert(0, 'RUNNAME', name)

        return beps_df
