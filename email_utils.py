import smtplib
from email.message import EmailMessage


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = "soundarmail0505@gmail.com"
SENDER_PASSWORD = "emud zska pyzp ccuz"


def send_invoice_email(to_email, purchase, balance_breakdown):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Purchase Invoice"
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        product_details = ""
        for item in purchase.items:
            product_details += f"""
Product ID   : {item.product_id}
Product Name : {item.product_name}
Quantity     : {item.quantity}
Total Price  : {item.total_price:.2f}
----------------------------------------
"""

        balance_text = ""
        for note, count in balance_breakdown.items():
            if count > 0:
                balance_text += f"{note} x {count}\n"

        email_body = f"""
Thank you for your purchase.

Invoice ID : {purchase.id}

{product_details}

Net Amount       : {purchase.net_price:.2f}
Balance Returned : {purchase.balance_amount:.2f}

Balance Denomination:
{balance_text}

Regards,
Billing Team
"""

        msg.set_content(email_body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print("Email sent successfully")

    except Exception as e:
        print("Email sending failed:", e)
