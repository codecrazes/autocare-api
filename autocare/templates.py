def create_confirmation_email_template(name, confirmation_link):
    subject = "Confirmação de E-mail"
    body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                }}
                .container {{
                    width: 80%;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #dddddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    font-size: 16px;
                    color: white;
                    background-color: #007BFF;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 20px;
                }}
                .button:hover {{
                    background-color: #0056b3;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Olá {name},</h2>
                <p>Obrigado por se cadastrar no nosso site! Para confirmar o seu e-mail, por favor clique no botão abaixo:</p>
                <a href="{confirmation_link}" class="button">Confirmar E-mail</a>
                <p>Se você não se cadastrou no nosso site, por favor ignore este e-mail.</p>
                <p>Atenciosamente,</p>
                <p>Equipe do Autocare</p>
                <div class="footer">
                    <p>Este é um e-mail automático, por favor não responda.</p>
                </div>
            </div>
        </body>
    </html>
    """  # noqa: E501

    return subject, body


def create_password_reset_email_template(name, reset_link):
    subject = "Redefinição de Senha"
    body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                }}
                .container {{
                    width: 80%;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #dddddd;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    font-size: 16px;
                    color: white;
                    background-color: #dc3545;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 20px;
                }}
                .button:hover {{
                    background-color: #c82333;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Olá {name},</h2>
                <p>Recebemos uma solicitação para redefinir a sua senha. Para prosseguir com a redefinição, por favor clique no botão abaixo:</p>
                <a href="{reset_link}" class="button">Redefinir Senha</a>
                <p>Se você não solicitou a redefinição de senha, por favor ignore este e-mail.</p>
                <p>Atenciosamente,</p>
                <p>Equipe do Autocare</p>
                <div class="footer">
                    <p>Este é um e-mail automático, por favor não responda.</p>
                </div>
            </div>
        </body>
    </html>
    """  # noqa: E501

    return subject, body
