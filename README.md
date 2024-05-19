Este projeto foi feito com o Raspberry pi 3 A+.

Como conectar ao Raspberry pi:
1. ligas o Raspberry pi com um transformador ou a 5V e 2.5A
2. Correr aplicação angry IP Scanner e procurar um host_name que diga Raspberry pi
   Caso seja a primeira vez:
  3. copiar esse IP e meter no PUTTY (user_name = Pi e pass = Pi)
  4. sudo raspi-config
  5. interface options
  6. enable VNC
7. inserir o ip no RealVNC viewer

Como correr o programa:
(no nosso caso temos as libs num virtual environmental)
1. cd Desktop
2. cd PIC
3. source env/bin/activate
4. python3 main.py

Como conectar o hardware
![esquema eletrico](https://github.com/miguel5andrade/PIC1_project/assets/109182326/c24ebe51-8938-42d8-ae0d-61d7fc987c15)

