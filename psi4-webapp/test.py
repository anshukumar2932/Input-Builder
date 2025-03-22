output_path=f"uploads/test_input.out"
with open(output_path, "r") as file:
    important_lines = file.read()

print(important_lines)  # Prints the file content exactly as it is
