BC_START_SYM = "130"
BC_STOP_SYM = "130"

format_control_code = "11"
sorting_code = "12345678"
user_information_string = "ABC123"

barcode = BC_START_SYM + format_control_code + sorting_code + user_information_string + BC_STOP_SYM

print("Generated Barcode:", barcode)