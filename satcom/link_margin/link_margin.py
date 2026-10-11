actual_cn_db = 22.37
required_cn_db = 10.0
reserve_db = 3.0

raw_margin_db = actual_cn_db - required_cn_db
remaining_margin_db = raw_margin_db - reserve_db

print(f"Actual C/N: {actual_cn_db:.2f} dB")
print(f"Required C/N: {required_cn_db:.2f} dB")
print(f"Raw link margin: {raw_margin_db:.2f} dB")
print(f"Reserve allowance: {reserve_db:.2f} dB")
print(f"Margin after reserve: {remaining_margin_db:.2f} dB")

if remaining_margin_db >= 0:
    print("Result: Meets illustrative requirement.")
else:
    print("Result: Does not meet illustrative requirement.")