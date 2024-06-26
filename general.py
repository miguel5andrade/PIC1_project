def list_to_integer(list_int):
    # Convert each integer to a string and concatenate them
    concatenated_string = ''.join(str(num) for num in list_int)

    # Convert the concatenated string back to an integer
    resulting_integer = int(concatenated_string)
    return resulting_integer

def split_integer_to_list(integer):
    # Convert the integer to a string
    integer_str = str(integer)
    
    # Convert each character back to an integer and collect them in a list
    integer_list = [int(char) for char in integer_str]
    
    return integer_list

def is_key_number(number):
    if number > 4 or number < 1:
        return 0
    else:
        return 1
    
