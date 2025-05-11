import qrcode
url = " https://df4e-2405-9800-b651-70a9-a975-a102-b9f5-ab30.ngrok-free.app"
qrcode.make(url).save("qr.png")