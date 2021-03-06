# icmm-reward
e-Reward generator for ICMM

## Install

    $ pip install -r requirements

## API Reference
**Get index page**

GET / 

Return: index.html

**Get runners info, Certificate and E-Coupon**

GET /api/runners/:bibNumber?pin=Tel4Digit

Return: Runner model

ex. /api/runners/1002?pin=9943

**Get certificate image**

GET /img/challengeCert/:bibNumber?pin=Tel4Digit

Return: raw image of challenge certificate

ex. /img/challengeCert/96?pin=9943

Certificate details:
- Runner Firstname & Lastname
- Full BIB (ex. E24-96)
- Challenge

**Get e-reward image**

GET /img/eReward/:templateId/:bibNumber?pin=Tel4Digit

Return: raw image of e-reward 

ex. 
- /img/eReward/1/96?pin=9943 (Get e-reward from sponsor1)
- /img/eReward/2/96?pin=9943 (Get e-reward from sponsor2)

e-Reward details:
- Runner Firstname & Lastname
- Full BIB as a reward code (ex. E24-96)