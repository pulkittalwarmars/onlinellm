import sys
import logging

def error_message_details(error,error_detail:sys):
    _,_,exc_tb=error_detail.exc_info() # this variable tells you where the exception has occured i.e. what file and what line
    
    file_name=exc_tb.tb_frame.f_code.co_filename ## this is in the documentation - this gets us the name of the file where the exception has occured
    
    line_number=exc_tb.tb_lineno ## gets us the line number where the error has occured

    error_message="Error occured in python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name,
        line_number,
        str(error)
    )

    return error_message

class CustomException(Exception):
    def __init__(self, error_message,error_detail:sys):
        super().__init__(error_message)
        self.error_message=error_message_details(error_message,error_detail=error_detail)

    def __str__(self) -> str:
        return self.error_message


## Test the custom exception
if __name__=="__main__":

    try:
        a=1/0
    except Exception as e:
        logging.info("CustomException divide by 0 error")
        raise CustomException(e,sys)