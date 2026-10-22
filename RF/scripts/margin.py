
def calculate_margin(available_db, required_db):
    return available_db - required_db

available_cn_db = 13.22
required_cn_db = 10.0

margin_db = calculate_margin(available_cn_db, required_cn_db)

print("RF-09: Link Margin")
print(f"Available C/N : {available_cn_db:.2f} dB")
print(f"Required C/N  : {required_cn_db:.2f} dB")
print(f"Link margin   : {margin_db:.2f} dB")

if margin_db > 0:
    print("Result: requirement met in this calculation.")
elif margin_db == 0:
    print("Result: exactly at the requirement.")
else:
    print("Result: requirement not met.")
