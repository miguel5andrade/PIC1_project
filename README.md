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
  cd Desktop
  cd PIC
  source env/bin/activate
  python3 main.py

Como conectar o hardware
![esquema eletrico](https://github.com/miguel5andrade/PIC1_project/assets/109182326/b59254ac-73ba-43d6-b0ee-8d7a61803ff5)
