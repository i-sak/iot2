# master
# 사용자 : 김이삭
github에 push시 입력해야할 name : i-sak
패스워드는 항상 사용하던 것으로 사용

# 1. webHook을 사용하기 위해서 ngrok를 실행한다.
./ngrok http 8080

# 2. webserver를 구동시킨다.
python3 serverRun.py

# 3-0 google 먼저 로그인 한다.
# 3. Dialogflow 홈페이지 접속한다.
Fulfillment 항목에 들어가서 Webhook에 ngrok에서 할당받은 링크를
걸어주어 webhook을 할 수 있게 한다.

# 4. ★★★
udp 서버를 통해 기기를 제어한다.
common 폴더의 udbserver.py를 실행한다.

지금은 기기가 없기 때문에 신호만 받을 수 있도록 웹서버 위에서 소켓 통신 테스트만 할 수 있도록 구축되어 있다.
웹서버 http://localhost/test 에서 소켓 통신 확인이 가능

추후 모든 소형 컴퓨터에서 실행하게 될 코드