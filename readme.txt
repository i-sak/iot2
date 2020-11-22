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

