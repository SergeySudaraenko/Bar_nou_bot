import qrcode

# ссылку бота
bot_url = "https://t.me/BarNouBot"

# Генерация QR-кода
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(bot_url)
qr.make(fit=True)

# Сохранение QR-кода в файл
img = qr.make_image(fill_color="black", back_color="white")
img.save("bot_qr_code.png")

print("QR-код создан и сохранен в 'bot_qr_code.png'.")
