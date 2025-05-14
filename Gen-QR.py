import qrcode
url = " https://51a8-1-47-78-145.ngrok-free.app"
qrcode.make(url).save("qr.png")